import boto3
import botocore
import botocore.exceptions

import psycopg2
import psycopg2.extras

import os

import config as CONFIG

import logging
logger = logging.getLogger(__name__)


def db_connection():
    
    return psycopg2.connect(
        user=CONFIG.CUMULUS_DBUSER,
        host=CONFIG.CUMULUS_DBHOST,
        dbname=CONFIG.CUMULUS_DBNAME,
        password=CONFIG.CUMULUS_DBPASS
    )


# TODO make all data access through RESTful API; Do not allow direct database connection
def write_database(entries):
    
    def dict_to_tuple(d):
        return tuple([d['datetime'], d['file'], d['product_id'], d['version']])
    
    values = [dict_to_tuple(e) for e in entries]

    try:
        conn = db_connection()
        c = conn.cursor()
        psycopg2.extras.execute_values(
            c, "INSERT INTO productfile (datetime, file, product_id, version) VALUES %s ON CONFLICT ON CONSTRAINT unique_product_version_datetime DO NOTHING", values,
        )
        conn.commit()
    except Exception as e:
        print(e)
    finally:
        c.close()
        conn.close()
    
    return len(entries)


# TODO make all data access through RESTful API; Do not allow direct database connection
def get_products():
    '''Map of <name>:<product_id> for all products in the database'''
    
    try:
        conn = db_connection()
        c = conn.cursor()
        c.execute("SELECT name, id from product")
        rows = c.fetchall()
    finally:
        c.close()
        conn.close()
    
    return { r[0]: r[1] for r in rows}


def get_infile(bucket, key, filepath):
    
    s3 = boto3.resource('s3')
    try:
        s3.Bucket(bucket).download_file(key, filepath)
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
    s3_client = boto3.resource('s3')

    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except botocore.exceptions.ClientError as e:
        logger.error('Unable to upload file to S3.')
        logger.error(e)
        return False
    return True