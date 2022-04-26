"""handle the messages coming from the worker thread
"""


import asyncio
import os

from botocore.exceptions import ClientError
from cumulus_geoproc import logger
from cumulus_geoproc.configurations import (
    APPLICATION_KEY,
    CUMULUS_API_URL,
    CUMULUS_PRODUCTS_BASEKEY,
    HTTP2,
)
from cumulus_geoproc.processors import geo_proc
from cumulus_geoproc.utils import boto, capi
from cumulus_geoproc.geoprocess.snodas import interpolate

this = os.path.basename(__file__)


def handle_message(geoprocess, GeoCfg, dst):
    """Handle the message from SQS determining what to do with it

    Geo processing is either 'snodas-interpolate' or 'incoming-file-to-cogs'

    Send payload to database for successful uploaded and processed file(s)

    Parameters
    ----------
    msg : sqs.Message
        SQS message from the Queue

    Returns
    -------
    list[dict]
        list of dictionary objects
    """
    proc_list = []

    if geoprocess == "snodas-interpolate":
        logger.debug(f"Geoprocess '{geoprocess}' working on '{GeoCfg.datetime}'")
        proc_list = asyncio.run(
            interpolate.snodas(
                GeoCfg,
                dst=dst,
            )
        )
    elif geoprocess == "incoming-file-to-cogs":
        # process and get resulting dictionary object defining the new grid
        # add acquirable id to each object in the list
        src = "/".join([GeoCfg.bucket, GeoCfg.key])
        logger.debug(f"Source: {src}")
        proc_list = geo_proc(
            plugin=GeoCfg.acquirable_slug,
            src=src,
            dst=dst,
            acquirable=GeoCfg.acquirable_slug,
        )

    return proc_list


def upload_notify(notices: list, bucket: str):
    responses = []
    payload = []

    # upload
    for notice in notices:
        # try to upload and continue if it doesn't returning only
        # what was successfully uploaded
        try:
            # try to upload to S3
            file = notice["file"]
            filename = os.path.basename(file)
            key = "/".join([CUMULUS_PRODUCTS_BASEKEY, notice["filetype"], filename])
            logger.debug(f"Notice key: {key}")

            # upload the file to S3
            if boto.s3_upload_file(file, bucket, key):
                logger.debug(f"S3 Upload: {file} -> {bucket}/{key}")

                # If successful on upload, notify cumulus, but
                # switch file to the key first
                notice["file"] = key

                responses.append({"key": key})
                payload.append(notice)
                logger.debug(f"Append Response: {responses[-1]}")
        except (KeyError, ClientError, Exception) as ex:
            logger.warning(f"{type(ex).__name__}: {this}: {ex}")
            continue

    # notify
    if len(payload) > 1:
        cumulus_api = capi.CumulusAPI(CUMULUS_API_URL, HTTP2)
        cumulus_api.endpoint = "productfiles"
        cumulus_api.query = {"key": APPLICATION_KEY}

        resp = asyncio.run(cumulus_api.post_(cumulus_api.url, payload=payload))
        responses.append({"upload": resp})

    return responses
