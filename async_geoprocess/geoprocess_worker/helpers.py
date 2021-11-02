import boto3
import botocore
import botocore.exceptions
from botocore.client import Config

from datetime import timezone

import os
import requests
import json

import config as CONFIG

import logging
logger = logging.getLogger(__name__)

def s3_kwargs():
    kwargs = {}
    if CONFIG.ENDPOINT_URL_S3:
        kwargs['endpoint_url'] = CONFIG.ENDPOINT_URL_S3
    
    if CONFIG.AWS_ACCESS_KEY_ID:
        kwargs['aws_access_key_id'] = CONFIG.AWS_ACCESS_KEY_ID
    
    if CONFIG.AWS_SECRET_ACCESS_KEY:
        kwargs['aws_secret_access_key'] = CONFIG.AWS_SECRET_ACCESS_KEY
    
    return kwargs

def s3_resource():
    kwargs = s3_kwargs()
    return boto3.resource('s3', **kwargs)

def s3_client():
    kwargs = s3_kwargs()
    return boto3.client('s3', **kwargs)

def write_database(entries):
    payload = [{'datetime': e['datetime'], 'file': e['file'], 'product_id': e['product_id'], 'version': e['version']} for e in entries]
    try:
        r = requests.post(
            f'{CONFIG.CUMULUS_API_URL}/productfiles?key={CONFIG.APPLICATION_KEY}',
            json=payload
        )
    except Exception as e:
        print(e)
    
    return len(entries)


def get_product_slugs():
    '''Map of <slug>:<product_id> for all products in the database'''
    
    try:
        r = requests.get(f'{CONFIG.CUMULUS_API_URL}/product_slugs')
    except Exception as e:
        print(e)
    
    return r.json()


def get_infile(bucket, key, filepath):
    
    resource = s3_resource()
    try:
        resource.Bucket(bucket).download_file(key, filepath)
        return os.path.abspath(filepath)

    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            logger.fatal(f'OBJECT DOES NOT EXIST: {key}')
            return None
        else:
            raise


def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    Copied from https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-uploading-files.html
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    # Upload the file    
    client = s3_client()

    try:
        response = client.upload_file(file_name, bucket, object_name)
    except botocore.exceptions.ClientError as e:
        logger.error('Unable to upload file to S3.')
        logger.error(e)
        return False
    return True