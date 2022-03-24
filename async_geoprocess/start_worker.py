"""main geoprocess worker thread

infinit while loop receives SQS messages and process them
"""

import json
import os
import shutil
from collections import namedtuple
from tempfile import TemporaryDirectory

import boto3

import geoprocess_worker.helpers as helpers
import geoprocess_worker.incoming_file_to_cogs as incoming_file_to_cogs

# import geoprocess_worker.snodas_interpolate as snodas_interpolate
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
logger.info(f"{queue=}")


def processed_files(file_list, acq_file_id):
    product_map = helpers.get_product_slugs()
    uploads = list()
    for file in file_list:
        ProcessorPayload = namedtuple("ProcessorPayload", file)(**file)
        # See that we have a valid
        if ProcessorPayload.filetype in product_map.keys():
            logger.debug("found acquirable: {ProcessorPayload.filetype}")
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
                        "product_id": product_map[ProcessorPayload.filetype],
                        "version": file_version,
                        "acquirablefile_id": acq_file_id,
                    }
                )
                logger.debug(f"file uploaded; payload appended; {uploads[-1]}")

    return uploads


def handle_message(msg):
    """Handle the message from SQS determining what to do with it

    Geo processing is either 'snodas-interpolate' or 'incoming-file-to-cogs'

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
    GeoCfg = namedtuple("GeoCfg", payload["geoprocess_config"])(
        **payload["geoprocess_config"]
    )

    logger.info(f"Geo Process: {geoprocess}")
    logger.info(f"Geo Processor Plugin: {GeoCfg.acquirable_slug}")

    with TemporaryDirectory() as temporary_directory:
        if geoprocess == "snodas-interpolate":
            pass
            # outfiles = snodas_interpolate.process(geoprocess_config, temporary_directory)
        elif geoprocess == "incoming-file-to-cogs":
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
        logger.debug(f"{successes=}")

        if len(successes) > 0:
            count = helpers.write_database(successes)

    return {"count": count, "productfiles": successes}


def start_worker():
    while True:
        messages = queue.receive_messages(
            MaxNumberOfMessages=MAX_Q_MESSAGES, WaitTimeSeconds=WAIT_TIME_SECONDS
        )
        if len(messages) == 0:
            logger.info("No messages")

        for message in messages:
            try:
                logger.debug(handle_message(message))
            except Exception as ex:
                logger.warning(ex)
            finally:
                message.delete()


if __name__ == "__main__":
    start_worker()
