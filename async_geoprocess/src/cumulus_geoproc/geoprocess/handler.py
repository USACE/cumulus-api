"""_summary_
"""


import asyncio
import os

import boto3
from botocore.exceptions import ClientError
from cumulus_geoproc import logger, utils
from cumulus_geoproc.configurations import (
    APPLICATION_KEY,
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    CUMULUS_API_URL,
    CUMULUS_MOCK_S3_UPLOAD,
    CUMULUS_PRODUCTS_BASEKEY,
    ENDPOINT_URL_S3,
    ENDPOINT_URL_SQS,
    HTTP2,
)
from cumulus_geoproc.processors import geo_proc
from cumulus_geoproc.utils.capi import CumulusAPI


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
    proc_list = list()

    if geoprocess == "snodas-interpolate":
        pass
        # GeoCfg = namedtuple("GeoCfg", payload["geoprocess_config"])(
        #     **payload["geoprocess_config"]
        # )
        # logger.debug(f"{GeoCfg=}")
        # logger.debug(f"{temporary_directory=}")
        # outfiles = snodas_interpolate.process(
        #     bucket=GeoCfg.bucket,
        #     date_time=GeoCfg.datetime,
        #     max_distance=int(GeoCfg.max_distance),
        #     outdir=temporary_directory,
        # )
    elif geoprocess == "incoming-file-to-cogs":
        # process and get resulting dictionary object defining the new grid
        # add acquirable id to each object in the list
        src = "/".join(["/vsis3_streaming", GeoCfg.bucket, GeoCfg.key])
        proc_list = geo_proc(
            plugin=GeoCfg.acquirable_slug,
            src=src,
            dst=dst,
            acquirable=GeoCfg.acquirable_slug,
        )

    return proc_list


def upload_notify(notices: list, bucket: str):
    responses = list()
    payload = list()

    # upload
    for notice in notices:
        # try to upload and continue if it doesn't returning only
        # what was successfully uploaded
        try:
            # try to upload to S3
            file = notice["file"]
            filename = os.path.basename(notice["file"])
            key = "/".join([CUMULUS_PRODUCTS_BASEKEY, notice["filetype"], filename])
            logger.debug(f"Notice key: {key}")

            # upload the file to S3
            utils.upload_file(file, bucket, key)
            logger.debug(f"S3 Upload: {file} -> {bucket}/{key}")

            # If successful on upload, notify cumulus, but
            # switch file to the key first
            notice["file"] = key

            responses.append({"key": key})
            payload.append(notice)
            logger.debug("Append Response: {responses[-1]}")
        except KeyError as ex:
            logger.warning(f"KeyError: {ex}")
            continue
        except ClientError as ex:
            logger.warning(f"ClientError: {ex}")
            continue
        except Exception as ex:
            logger.warning(ex)
            continue

    # notify
    if len(payload) > 1:
        cumulus_api = CumulusAPI(CUMULUS_API_URL, HTTP2)
        cumulus_api.endpoint = "productfiles"
        cumulus_api.query = {"key": APPLICATION_KEY}

        resp = asyncio.run(cumulus_api.post(cumulus_api.url, payload=payload))
        responses.append({"upload": resp})

    return responses
