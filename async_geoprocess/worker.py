"""main geoprocess worker thread

infinit while loop receives SQS messages and process them
"""

import asyncio
import json
import os
import time
from collections import namedtuple
from tempfile import TemporaryDirectory

import boto3

from cumulus_geoproc import logger, utils
from cumulus_geoproc.configurations import (
    AWS_ACCESS_KEY_ID,
    AWS_REGION_SQS,
    AWS_SECRET_ACCESS_KEY,
    CUMULUS_API_URL,
    ENDPOINT_URL_SQS,
    HTTP2,
    MAX_Q_MESSAGES,
    PRODUCT_FILE_VERSION,
    QUEUE_NAME,
    USE_SSL,
    WAIT_TIME_SECONDS,
)
from cumulus_geoproc.geoprocess import handler
from cumulus_geoproc.utils.capi import CumulusAPI


def start_worker():
    """starting the worker thread"""
    start = time.time()
    # initialize product slug list
    try:
        cumulus_api = CumulusAPI(CUMULUS_API_URL, HTTP2)
        cumulus_api.endpoint = "product_slugs"
        resp = asyncio.run(cumulus_api.get(cumulus_api.url))
        PRODUCT_MAP = resp.json()
        logger.debug("Initialize Product Slug -> UUID mapping'%s'" % PRODUCT_MAP)
    except Exception as ex:
        return ex

    # aws_access_key_id, aws_secret_access_key, aws_default_region, etc
    # set as env vars for local dev.  IAM role used for implementation

    sqs = boto3.resource(
        service_name="sqs",
        endpoint_url="http://elasticmq:9324",
        region_name="us-east-1",
        aws_secret_access_key="AKIAIOSFODNN7EXAMPLE",
        aws_access_key_id="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
        use_ssl=False,
    )
    # if AWS_ACCESS_KEY_ID is None:
    #     # Running in AWS Using IAM Role for Credentials
    #     if ENDPOINT_URL_SQS:
    #         sqs = boto3.resource("sqs", endpoint_url=ENDPOINT_URL_SQS)
    #     else:
    #         sqs = boto3.resource("sqs")
    # else:
    #     # Local Testing
    #     # ElasticMQ with Credentials via AWS_ environment variables
    #     sqs = boto3.resource(
    #         "sqs",
    #         endpoint_url=ENDPOINT_URL_SQS,
    #         region_name=AWS_REGION_SQS,
    #         aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    #         aws_access_key_id=AWS_ACCESS_KEY_ID,
    #         use_ssl=USE_SSL,
    #     )

    # Incoming Requests
    queue = sqs.get_queue_by_name(QueueName=QUEUE_NAME)

    logger.info(
        "%(spacer)s Starting the worker thread %(spacer)s" % {"spacer": "*" * 20}
    )
    logger.info("Queue: %s" % queue)

    while True:
        # check for updated product mapping each hour
        if (time.time() - start) > 3600:
            cumulus_api.endpoint = "product_slugs"
            resp = asyncio.run(cumulus_api.get(cumulus_api.url))
            PRODUCT_MAP = resp.json()

        messages = queue.receive_messages(
            MaxNumberOfMessages=MAX_Q_MESSAGES, WaitTimeSeconds=WAIT_TIME_SECONDS
        )
        if len(messages) == 0:
            logger.info("No messages")

        for message in messages:
            try:
                logger.info("%(spacer)s new message %(spacer)s" % {"spacer": "*" * 20})
                # parse message to payload as json object
                payload = json.loads(message.body)
                # get processor and its configurations from the message
                geoprocess = payload["geoprocess"]
                GeoCfg = namedtuple("GeoCfg", payload["geoprocess_config"])(
                    **payload["geoprocess_config"]
                )
                # setting acquirablefile id for later processing
                acquirablefile_id = (
                    GeoCfg.acquirablefile_id
                    if hasattr(GeoCfg, "acquirablefile_id")
                    else None
                )

                logger.info(f"Geo Process: {geoprocess}")
                logger.info(f"Geo Processor Plugin: {GeoCfg.acquirable_slug}")
                logger.debug(f"Message Payload: {payload}")

                # create a temporary directory and release in final exception
                dst = TemporaryDirectory()
                logger.debug(f"Temporary Directory: {dst.name}")

                # handle the message getting a list of json objects
                processed = handler.handle_message(geoprocess, GeoCfg, dst.name)

                # update processed messages with additional attributes
                # set product version is set to None from processor
                # KeyError for slug id not available allows for the loop to continue
                product_versioning = lambda p: PRODUCT_FILE_VERSION if p is None else p
                processed_ = list()
                for item in processed:
                    try:
                        item_ = {
                            **item,
                            **{
                                "acquirablefile_id": acquirablefile_id,
                                "product_id": PRODUCT_MAP[GeoCfg.acquirable_slug],
                                "version": product_versioning(item["version"]),
                            },
                        }
                        processed_.append(item_)
                        logger.debug(f"New processed dict item: {processed_[-1]}")
                    except KeyError as ex:
                        logger.warning(ex)
                        continue

                # notify cumulus of the processed files
                logger.info(f"Attempt to notify {len(processed_)} processed product(s)")
                resp = handler.upload_notify(notices=processed_, bucket=GeoCfg.bucket)
                logger.info(resp)
            except Exception as ex:
                logger.warning(ex)
            finally:
                dst = None
                message.delete()


if __name__ == "__main__":
    msg = start_worker()
    logger.critical(msg)
