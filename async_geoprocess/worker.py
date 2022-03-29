"""main geoprocess worker thread

infinit while loop receives SQS messages and process them
"""

import json
import os
import shutil
import time
from collections import namedtuple
from tempfile import TemporaryDirectory

import boto3

import geoprocess_worker.helpers as helpers
import geoprocess_worker.incoming_file_to_cogs as incoming_file_to_cogs
import geoprocess_worker.snodas_interpolate as snodas_interpolate
from geoprocess_worker import (
    AWS_ACCESS_KEY_ID,
    AWS_REGION_SQS,
    AWS_SECRET_ACCESS_KEY,
    CUMULUS_MOCK_S3_UPLOAD,
    ENDPOINT_URL_SQS,
    MAX_Q_MESSAGES,
    QUEUE_NAME,
    USE_SSL,
    WAIT_TIME_SECONDS,
    WRITE_TO_BUCKET,
    logger,
)

PRODUCT_MAP = helpers.get_product_slugs()
logger.debug("Initialize Product Slug -> UUID mapping'%s'" % PRODUCT_MAP)


def update_product_map():
    if PRODUCT_MAP == helpers.get_product_slugs():
        return False
    else:
        PRODUCT_MAP = helpers.get_product_slugs()
        return True


def processed_files(file_list: list, acq_file_id: str):
    """Send processed files to their respective S3 bucket and record
    its payload information for the cumulus database

    Parameters
    ----------
    file_list : List[dict]
        list of dictionaries produced by the processor
    acq_file_id : str
        acquirable file id

    Returns
    -------
    List[dict]
        list of dictionaries describing successful grid transforms
    """

    uploads = list()
    for file in file_list:
        ProcessorPayload = namedtuple("ProcessorPayload", file)(**file)
        # See that we have a valid
        if ProcessorPayload.filetype in PRODUCT_MAP.keys():
            logger.info(f"found acquirable: {ProcessorPayload.filetype}")
            # Write output files to different bucket
            write_key = "cumulus/products/{}/{}".format(
                ProcessorPayload.filetype, os.path.basename(ProcessorPayload.file)
            )
            if CUMULUS_MOCK_S3_UPLOAD:
                # Mock good upload to S3
                upload_success = True
                # Copy file to tmp directory on host
                # shutil.copy2 will overwrite a file if it already exists.
                shutil.copy2(ProcessorPayload.file, "/tmp")
            else:
                upload_success = helpers.upload_file(
                    ProcessorPayload.file, WRITE_TO_BUCKET, write_key
                )

            # Assign the acquirablefile_id to the productfile if
            # available in the georprocess_config message
            if upload_success:
                file_version = (
                    file["version"] if not None else "1111-11-11T11:11:11.11Z"
                )
                uploads.append(
                    {
                        "datetime": file["datetime"],
                        "file": write_key,
                        "product_id": PRODUCT_MAP[ProcessorPayload.filetype],
                        "version": file_version,
                        "acquirablefile_id": acq_file_id,
                    }
                )
                logger.debug(f"file uploaded; payload appended; {uploads[-1]}")

    return uploads


def handle_message(msg):
    """Handle the message from SQS determining what to do with it

    Geo processing is either 'snodas-interpolate' or 'incoming-file-to-cogs'

    Send payload to database for successful uploaded and processed file(s)

    Parameters
    ----------
    msg : sqs.Message
        SQS message from the Queue

    Returns
    -------
    dict
        dictionary with messages
    """
    payload = json.loads(msg.body)
    geoprocess = payload["geoprocess"]

    logger.info(f"Geo Process: {geoprocess}")

    with TemporaryDirectory() as temporary_directory:
        if geoprocess == "snodas-interpolate":
            GeoCfg = namedtuple("GeoCfg", payload["geoprocess_config"])(
                **payload["geoprocess_config"]
            )
            logger.debug(f"{GeoCfg=}")
            logger.debug(f"{temporary_directory=}")
            outfiles = snodas_interpolate.process(
                bucket=GeoCfg.bucket,
                date_time=GeoCfg.datetime,
                max_distance=int(GeoCfg.max_distance),
                outdir=temporary_directory,
            )
        elif geoprocess == "incoming-file-to-cogs":
            GeoCfg = namedtuple("GeoCfg", payload["geoprocess_config"])(
                **payload["geoprocess_config"]
            )

            logger.debug(f"{GeoCfg=}")
            logger.debug(f"{temporary_directory=}")
            logger.info(f"Geo Processor Plugin: {GeoCfg.acquirable_slug}")

            outfiles = incoming_file_to_cogs.process(
                bucket=GeoCfg.bucket,
                key=GeoCfg.key,
                plugin=GeoCfg.acquirable_slug,
                outdir=temporary_directory,
            )

        acquirablefile_id = (
            GeoCfg.acquirablefile_id if hasattr(GeoCfg, "acquirablefile_id") else None
        )

        successes = processed_files(file_list=outfiles, acq_file_id=acquirablefile_id)
        logger.debug(f"Successfully Processed Files: {successes}")

        count = helpers.write_database(successes)

        return {"count": count, "productfiles": successes}


def start_worker():
    start = time.time()
    """starting the worker thread"""
    if AWS_ACCESS_KEY_ID is None:
        # Running in AWS Using IAM Role for Credentials
        if ENDPOINT_URL_SQS:
            CLIENT = boto3.resource("sqs", endpoint_url=ENDPOINT_URL_SQS)
        else:
            CLIENT = boto3.resource("sqs")
    else:
        # Local Testing
        # ElasticMQ with Credentials via AWS_ environment variables
        CLIENT = boto3.resource(
            "sqs",
            endpoint_url=ENDPOINT_URL_SQS,
            region_name=AWS_REGION_SQS,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            use_ssl=USE_SSL,
        )

    # Incoming Requests
    queue = CLIENT.get_queue_by_name(QueueName=QUEUE_NAME)

    logger.info(
        "%(spacer)s Starting the worker thread %(spacer)s" % {"spacer": "*" * 20}
    )
    logger.info("Queue: %s" % queue)

    while True:
        # check for updated product mapping each hour
        if (time.time() - start) > 3600:
            PRODUCT_MAP = helpers.get_product_slugs()
            start = time.time()
            logger.info("Product mapping updated")

        messages = queue.receive_messages(
            MaxNumberOfMessages=MAX_Q_MESSAGES, WaitTimeSeconds=WAIT_TIME_SECONDS
        )
        if len(messages) == 0:
            logger.info("No messages")

        for message in messages:
            try:
                logger.info("%(spacer)s new message %(spacer)s" % {"spacer": "*" * 20})
                logger.debug(handle_message(message))
            except Exception as ex:
                logger.warning(ex)
            finally:
                message.delete()


if __name__ == "__main__":
    start_worker()
