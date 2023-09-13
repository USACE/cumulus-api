#!/usr/bin/python3

import json
import multiprocessing
import os
from pathlib import Path
import shutil
import traceback
from collections import namedtuple
from tempfile import TemporaryDirectory

import boto3
from codetiming import Timer
import requests

from cumulus_packager import logger
from cumulus_packager.configurations import (
    APPLICATION_KEY,
    AWS_ACCESS_KEY_ID,
    AWS_DEFAULT_REGION,
    AWS_SECRET_ACCESS_KEY,
    CUMULUS_API_URL,
    ENDPOINT_URL_SQS,
    MAX_Q_MESSAGES,
    QUEUE_NAME_PACKAGER,
    WAIT_TIME_SECONDS,
    WRITE_TO_BUCKET,
)
from cumulus_packager.packager import handler
from cumulus_packager.utils import capi
from cumulus_packager.utils.boto import s3_upload_file

this = os.path.basename(__file__)


def handle_message(message):
    try:
        logger.info("%(spacer)s new message %(spacer)s" % {"spacer": "*" * 20})

        # parse message to payload as json object and get the download id
        message_body = message.body
        logger.debug(f"{message_body=}")

        download_id = json.loads(message.body)["id"]
        logger.debug(f"Download ID: {download_id}")

        # get the payload from the download endpoint with the download_id
        # and expand that to a namedtuple
        resp = requests.request(
            "GET",
            url=f"{CUMULUS_API_URL}/downloads/{download_id}/packager_request",
            params={"key": APPLICATION_KEY},
        )

        if resp.status_code != 200:
            raise Exception(resp)

        # create a temporary directory and release in final exception
        dst = TemporaryDirectory()
        logger.debug(f"Temporary Directory: {dst.name}")

        # response json to namedtuple
        _r = resp.json()
        PayloadResp = namedtuple("PayloadResp", _r)(**_r)

        # If download request contains 0 grids, set status to 'FAILED' and return
        if len(PayloadResp.contents) == 0:
            handler.update_status(download_id, handler.PACKAGE_STATUS["FAILED"], 0)
            # TODO: Add new package_status in database to represent EMPTY condition
            logger.info(f"Download Failed Due to Empty Contents: {download_id}")
        else:
            package_file = handler.handle_message(PayloadResp, dst.name)

            if package_file:
                # Upload File to S3
                logger.debug(f"ID '{download_id}'; Packaging Successful")
                t1 = Timer(logger=None)
                t1.start()
                s3_upload_worked = s3_upload_file(
                    package_file, WRITE_TO_BUCKET, PayloadResp.output_key
                )
                elapsed_time = t1.stop()
                if s3_upload_worked:
                    logger.info(
                        f"S3 upload '{PayloadResp.output_key}' in {elapsed_time:.4f} seconds"
                    )
                    handler.update_status(
                        download_id,
                        handler.PACKAGE_STATUS["SUCCESS"],
                        100,
                        PayloadResp.output_key,
                        # Manifest JSON
                        {
                            "size_bytes": os.path.getsize(package_file),
                            "filecount": len(PayloadResp.contents),
                        },
                    )
                else:
                    handler.update_status(
                        download_id, handler.PACKAGE_STATUS["FAILED"], 51
                    )
            else:
                logger.critical(
                    f"Failed to package or upload to S3; Download {download_id}"
                )

    except Exception as ex:
        logger.warning(
            f"{type(ex).__name__} - {this} - {ex} - {traceback.format_exc()}"
        )
        # Set download status to failed and percent complete to 0; This is a workaround
        # this should set status to failed and leave percent as-is. TODO: Implement capability
        # in cumulus-api to support progress updates that include status (without percent complete).
        handler.update_status(download_id, handler.PACKAGE_STATUS["FAILED"], 50)
    finally:
        package_file = None
        if os.path.exists(dst.name):
            shutil.rmtree(dst.name, ignore_errors=True)
        dst = None
        message.delete()

    return 0


if __name__ == "__main__":
    # aws_access_key_id, aws_secret_access_key, aws_default_region, etc
    # set as env vars for local dev.  IAM role used for implementation
    sqs = boto3.resource(
        service_name="sqs",
        endpoint_url=ENDPOINT_URL_SQS,
        region_name=AWS_DEFAULT_REGION,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
    )

    # Incoming Requests
    queue = sqs.get_queue_by_name(QueueName=QUEUE_NAME_PACKAGER)

    logger.info(
        "%(spacer)s Starting the packager thread %(spacer)s" % {"spacer": "*" * 20}
    )
    logger.info("Queue: %s" % queue)

    while True:
        messages = queue.receive_messages(
            MaxNumberOfMessages=MAX_Q_MESSAGES, WaitTimeSeconds=WAIT_TIME_SECONDS
        )
        for message in messages:
            p = multiprocessing.Process(target=handle_message, args=(message,))
            p.start()
            p.join()
