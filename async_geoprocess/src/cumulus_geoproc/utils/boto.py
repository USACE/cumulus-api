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

this = os.path.basename(__file__)


def s3_upload_file(file_name: str, bucket: str, key: str = None):
    """Wrapper supporting S3 uploading a file

    Parameters
    ----------
    file_name : str
        file to upload
    bucket : str
        S3 bucket
    key : str, optional
        S3 object key, by default None

    Returns
    -------
    bool
        boolean describing successful upload

    Raises
    ------
    Exception
        ClientError
    """
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
        logger.error(f"{type(ex).__name__}: {this}: {ex} - key: {key}")
        return False
    return True


def s3_download_file(bucket: str, key: str, dst: str = "/tmp", prefix: str = None):
    """Wrapper supporting S3 downloading a file

    Parameters
    ----------
    bucket : str
        S3 Bucket
    key : str
        S3 key object
    prefix : str, optional
        Add prefix to filename, by default ""
    dst : str, optional
        FQP to temporary directory, by default "/tmp"

    Returns
    -------
    str | False
        FQPN to downloaded file | False if failed

    Raises
    ------
    Exception
        ClientError
    """
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
    except ClientError as ex:
        logger.error(f"{type(ex).__name__}: {this}: {ex} - key: {key}")
        return
    return filename


def boto3_resource(**kwargs):
    """Define boto3 resource

    Returns
    -------
    boto3.resource
        resource object with default options with or without user defined attributes
    """
    kwargs_ = {
        "aws_access_key_id": AWS_ACCESS_KEY_ID,
        "aws_secret_access_key": AWS_SECRET_ACCESS_KEY,
        "region_name": AWS_DEFAULT_REGION,
        **kwargs,
    }

    return boto3.resource(**kwargs_)

def boto3_client(**kwargs):
    """Define boto3 client

    Returns
    -------
    boto3.client
        client object with default options with or without user defined attributes
    """
    kwargs_ = {
        "aws_access_key_id": AWS_ACCESS_KEY_ID,
        "aws_secret_access_key": AWS_SECRET_ACCESS_KEY,
        "region_name": AWS_DEFAULT_REGION,
        **kwargs,
    }

    return boto3.client(**kwargs_)
