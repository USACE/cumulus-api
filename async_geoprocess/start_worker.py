"""main geoprocess worker thread

infinit while loop receives SQS messages and process them
"""

from collections import namedtuple
import json
import shutil
from tempfile import TemporaryDirectory

import boto3

# PROCESSORS
from .geoprocess_worker import (
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
    SignalHandler,
    helpers,
    logger,
    p_incoming_file_to_cogs,
    p_snodas_interpolate,
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


# """Converts JSON-Formatted message string to dictionary and calls geoprocessor"""
"""
"""


def handle_message(msg):
    """Handle the message from SQS determining what to do with it

    Geo processing is either 'snodas-interpolate' or 'incoming-file-to-cogs'

    {
        "geoprocess": "incoming-file-to-cogs",
        "geoprocess_config": {
            "acquirablefile_id": "11a69c52-3a59-4c50-81a6-eba26e6573d4",
            "acquirable_id": "2429db9a-9872-488a-b7e3-de37afc52ca4",
            "acquirable_slug": "cbrfc-mpe",
            "bucket": "castle-data-develop",
            "key": "cumulus/acquirables/cbrfc-mpe/xmrg0322202216z.grb"
        }
    }

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
    GeoCfg = namedtuple("GeoCfg", payload["geoprocess_config"])(
        **payload["geoprocess_config"]
    )

    geoprocess = payload["geoprocess"]

    with TemporaryDirectory() as td:

        if geoprocess == "snodas-interpolate":
            outfiles = p_snodas_interpolate.process(geoprocess_config, td)
        elif geoprocess == "incoming-file-to-cogs":
            outfiles = p_incoming_file_to_cogs.process(geoprocess_config, td)
        else:
            logger.critical("processor not implemented")
            return {}

        # Keep track of successes to send as single database query at the end
        successes = []
        # Valid products in the database
        product_map = helpers.get_product_slugs()
        for _f in outfiles:
            # See that we have a valid
            if _f["filetype"] in product_map.keys():
                # Write output files to different bucket
                write_key = "cumulus/products/{}/{}".format(
                    _f["filetype"], _f["file"].split("/")[-1]
                )
                if CUMULUS_MOCK_S3_UPLOAD:
                    # Mock good upload to S3
                    upload_success = True
                    # Copy file to tmp directory on host
                    # shutil.copy2 will overwrite a file if it already exists.
                    shutil.copy2(_f["file"], "/tmp")
                else:
                    upload_success = helpers.upload_file(
                        _f["file"], WRITE_TO_BUCKET, write_key
                    )

                # Assign the acquirablefile_id to the productfile if
                # available in the georprocess_config message
                _acquirablefile_id = (
                    geoprocess_config["acquirablefile_id"]
                    if "acquirablefile_id" in geoprocess.keys()
                    else None
                )

                # Write Productfile Entry to Database
                if upload_success:
                    successes.append(
                        {
                            "product_id": product_map[_f["filetype"]],
                            "datetime": _f["datetime"],
                            "file": write_key,
                            "acquirablefile_id": _acquirablefile_id,
                            "version": _f["version"]
                            if _f["version"] is not None
                            else "1111-11-11T11:11:11.11Z",
                        }
                    )

        count = helpers.write_database(successes)

    return {"count": count, "productfiles": successes}


if __name__ == "__main__":
    signal_handler = SignalHandler()
    while signal_handler.received_signal:
        messages = queue.receive_messages(
            MaxNumberOfMessages=MAX_Q_MESSAGES, WaitTimeSeconds=WAIT_TIME_SECONDS
        )
        if len(messages) == 0:
            logger.info("No messages")

        for message in messages:
            logger.debug(handle_message(message))
            message.delete()
