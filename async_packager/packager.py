#!/usr/bin/python3

import asyncio
import json
import multiprocessing
import os
import shutil
import time
import traceback
from collections import deque, namedtuple
from tempfile import TemporaryDirectory

import boto3

from cumulus_packager import logger
from cumulus_packager.configurations import (
    APPLICATION_KEY,
    AWS_ACCESS_KEY_ID,
    AWS_DEFAULT_REGION,
    AWS_SECRET_ACCESS_KEY,
    CUMULUS_API_URL,
    ENDPOINT_URL_SQS,
    HTTP2,
    MAX_Q_MESSAGES,
    QUEUE_NAME_PACKAGER,
    WAIT_TIME_SECONDS,
    WRITE_TO_BUCKET,
)
from cumulus_packager.packager import handler
from cumulus_packager.utils import capi
from cumulus_packager.utils.boto import s3_upload_file

this = os.path.basename(__file__)


def start_packager():
    """Starting the packager thread"""
    perf_queue = deque(maxlen=1000)

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

        if len(messages) == 0:
            try:
                average_sec = sum(perf_queue) / len(perf_queue)
                logger.info(
                    f"Process Message: Avg {average_sec:0.4f} (sec); Deque Size {len(perf_queue)}"
                )
            except ZeroDivisionError as ex:
                logger.info(f"{type(ex).__name__} - {this} - {ex}")
        for message in messages:
            try:
                start_message = time.perf_counter()

                logger.info("%(spacer)s new message %(spacer)s" % {"spacer": "*" * 20})

                # parse message to payload as json object and get the download id
                download_id = json.loads(message.body)["id"]
                logger.debug(f"Download ID: {download_id}")

                # get the payload from the download endpoint with the download_id
                # and expand that to a namedtuple
                cumulus_api = capi.CumulusAPI(CUMULUS_API_URL, HTTP2)
                cumulus_api.endpoint = f"downloads/{download_id}/packager_request"
                cumulus_api.query = {"key": APPLICATION_KEY}
                resp = asyncio.run(cumulus_api.get_(cumulus_api.url))

                # logger.debug(f"Request Response: {resp.json()}")

                if resp.status_code != 200:
                    raise Exception(resp)

                # create a temporary directory and release in final exception
                dst = TemporaryDirectory()
                logger.debug(f"Temporary Directory: {dst.name}")

                # response json to namedtuple
                PayloadResp = namedtuple("PayloadResp", resp.json())(**resp.json())

                mpq = multiprocessing.Queue()
                mpq.put({"return": None})
                mp = multiprocessing.Process(
                    target=handler.handle_message, args=(mpq, PayloadResp, dst.name)
                )
                mp.start()
                mp.join()
                package_file = mpq.get()["return"]

                # if package_file := handler.handle_message(PayloadResp, dst.name):
                if package_file:
                    logger.debug(f"ID '{download_id}' processed")
                    if s3_upload_file(
                        package_file,
                        WRITE_TO_BUCKET,
                        PayloadResp.output_key,
                    ):
                        handler.package_status(
                            download_id,
                            handler.PACKAGE_STATUS[1],
                            1,
                            PayloadResp.output_key,
                        )
                        logger.debug(f"'{package_file}' uploaded")
                    else:
                        raise Exception(f"'{package_file}' failed to upload")
                else:
                    raise Exception(f"ID '{download_id} NOT processed")

            except Exception as ex:
                handler.package_status(download_id, handler.PACKAGE_STATUS[-1], 0)
                logger.warning(
                    f"{type(ex).__name__} - {this} - {ex} - {traceback.format_exc()}"
                )
            finally:
                if os.path.exists(dst.name):
                    shutil.rmtree(dst.name, ignore_errors=True)
                dst = None
                message.delete()
                perf_queue.append(perf_time := time.perf_counter() - start_message)
                logger.debug(f"Handle Message Time: {perf_time} (sec)")


if __name__ == "__main__":
    start_packager()
