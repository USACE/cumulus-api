"""_summary_
"""

import os
from signal import SIGINT, SIGTERM, signal
import boto3
from botocore.exceptions import ClientError
from cumulus_geoproc import logger
from cumulus_geoproc.configurations import (
    AWS_ACCESS_KEY_ID,
    AWS_DEFAULT_REGION,
    AWS_REGION_SQS,
    AWS_SECRET_ACCESS_KEY,
    ENDPOINT_URL_S3,
    ENDPOINT_URL_SQS,
    USE_SSL,
)

# ------------------------- #
# Signal Handler
# ------------------------- #
class SignalHandler:
    def __init__(self):
        self.received_signal = False
        signal(SIGINT, self._signal_handler)
        signal(SIGTERM, self._signal_handler)

    def _signal_handler(self, signal, frame):
        print(f"handling signal {signal}, exiting gracefully")
        self.received_signal = True


def file_extension(file, ext=".tif"):
    if not ext.startswith("."):
        ext = "." + ext
    return os.path.splitext(file)[0] + ext


def s3_upload_file(file_name, bucket, key=None):
    # If S3 object_name was not specified, use file_name
    if key is None:
        key = os.path.basename(file_name)

    # Upload the file
    try:
        # if (s3 := boto3_resource("s3")) is None:
        #     raise Exception(ClientError)
        # s3.meta.client.upload_file(Filename=file_name, Bucket=bucket, Key=key)
        logger.debug(f"{file_name}\t{bucket=}\t{key=}")
    except ClientError as ex:
        logger.error(ex)
        return False
    return True


def boto3_resource(**kwargs):
    kwargs_ = {
        "aws_access_key_id": os.environ.get("AWS_ACCESS_KEY_ID", default=None),
        "aws_secret_access_key": os.environ.get("AWS_SECRET_ACCESS_KEY", default=None),
        **kwargs,
    }

    return boto3.resource(**kwargs_)


def upload_file(file_name, bucket, object_name=None):
    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    # Upload the file
    s3 = boto3_resource(
        service_name="s3",
        endpoint_url=os.environ.get("ENDPOINT_URL_S3", default=None),
    )

    try:
        s3.meta.client.upload_file(file_name, bucket, object_name)
    except ClientError as ex:
        logger.error(ex)
        return False
    return True
