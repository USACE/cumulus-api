"""Cumulus utilities helping with S3 functionality
"""

import os

import boto3
from botocore.exceptions import ClientError
from cumulus_geoproc import logger
from cumulus_geoproc.configurations import (
    AWS_ACCESS_KEY_ID,
    AWS_DEFAULT_REGION,
    AWS_SECRET_ACCESS_KEY,
    ENDPOINT_URL_S3,
)


def s3_upload_file(file_name, bucket, key=None):
    # If S3 object_name was not specified, use file_name
    if key is None:
        key = os.path.basename(file_name)

    # Upload the file
    try:
        if (
            s3 := boto3_resource(
                service_name="s3",
                endpoint_url=ENDPOINT_URL_S3,
            )
        ) is None:
            raise Exception(ClientError)
        s3.meta.client.upload_file(Filename=file_name, Bucket=bucket, Key=key)
        logger.debug(f"{file_name}\t{bucket=}\t{key=}")
    except ClientError as ex:
        logger.error(ex)
        return False
    return True


def s3_download_file(bucket: str, key: str, prefix: str = None, dst: str = "/tmp"):
    file = os.path.basename(key)
    file = prefix + "-" + file if prefix else file

    filename = os.path.join(dst, file)
    logger.debug(f"S3 Download File: {filename}")

    # download the file
    try:
        if (
            s3 := boto3_resource(
                service_name="s3",
                endpoint_url=ENDPOINT_URL_S3,
            )
        ) is None:
            raise Exception(ClientError)
        s3.meta.client.download_file(
            Bucket=bucket,
            Key=key,
            Filename=filename,
        )
        logger.debug(f"{bucket=}\t{key=}\t{filename=}")
    except ClientError as ex:
        logger.error(ex)
        return False
    return filename


def boto3_resource(**kwargs):
    kwargs_ = {
        "aws_access_key_id": AWS_ACCESS_KEY_ID,
        "aws_secret_access_key": AWS_SECRET_ACCESS_KEY,
        "region_name": AWS_DEFAULT_REGION,
        **kwargs,
    }

    return boto3.resource(**kwargs_)
