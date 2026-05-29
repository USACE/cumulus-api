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


def handle_message(message_body):
    package_file = None
    dst = None
    try:
        logger.info("%(spacer)s new message %(spacer)s" % {"spacer": "*" * 20})
        logger.debug(f"{message_body=}")

        download_id = json.loads(message_body)["id"]
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

        # get the full download record to retrieve the requested product_id list
        dl_resp = requests.request(
            "GET",
            url=f"{CUMULUS_API_URL}/downloads/{download_id}",
            params={"key": APPLICATION_KEY},
        )
        requested_product_ids = dl_resp.json().get("product_id", []) if dl_resp.status_code == 200 else []

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
            logger.info(f'Empty Contents: No products selected in the request for download ID "{download_id}"')
        else:
            writer_result = handler.handle_message(PayloadResp, dst.name)

            if writer_result:
                package_file = writer_result["file"]
                product_stats = writer_result["product_stats"]

                # Fill in products that had 0 files in contents
                for pid in requested_product_ids:
                    if str(pid) not in product_stats:
                        product_stats[str(pid)] = {"expected": 0, "successful": 0}

                # Determine status from per-product stats
                total_expected = sum(ps["expected"] for ps in product_stats.values())
                total_successful = sum(ps["successful"] for ps in product_stats.values())
                all_products_have_data = all(ps["expected"] > 0 for ps in product_stats.values())

                if total_successful == total_expected and all_products_have_data:
                    status_key = "SUCCESS"
                else:
                    status_key = "PARTIAL_SUCCESS"

                # Upload File to S3
                logger.debug(f'Packaging {status_key.lower()} for download ID "{download_id}" ({total_successful}/{total_expected} files)')
                t1 = Timer(logger=None)
                t1.start()
                s3_upload_worked = s3_upload_file(
                    package_file, WRITE_TO_BUCKET, PayloadResp.output_key
                )
                elapsed_time = t1.stop()
                if s3_upload_worked:
                    logger.info(
                        f'S3 upload "{PayloadResp.output_key}" in {elapsed_time:.4f} seconds'
                    )
                    handler.update_status(
                        download_id,
                        handler.PACKAGE_STATUS[status_key],
                        100,
                        PayloadResp.output_key,
                        # Manifest JSON with per-product stats
                        {
                            "size_bytes": os.path.getsize(package_file),
                            "filecount": total_expected,
                            "filecount_successful": total_successful,
                            "product_stats": product_stats,
                        },
                    )
                else:
                    handler.update_status(
                        download_id, handler.PACKAGE_STATUS["FAILED"], 51
                    )
            else:
                logger.critical(
                    f'Failed to package or upload to S3 download ID "{download_id}"'
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
        if dst is not None and os.path.exists(dst.name):
            shutil.rmtree(dst.name, ignore_errors=True)
            dst = None

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
            p = multiprocessing.Process(target=handle_message, args=(message.body,))
            p.start()
            p.join()
            message.delete()
