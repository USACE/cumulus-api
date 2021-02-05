import importlib
import json
import logging
import os
import tempfile
from urllib.parse import unquote_plus
import requests

import boto3
import botocore
import botocore.exceptions

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


# Get WRITE_TO_BUCKET; Fail fast if not provided
WRITE_TO_BUCKET = os.getenv("WRITE_TO_BUCKET", default="")
if WRITE_TO_BUCKET == "":
    logging.fatal('Missing Environment Variable "WRITE_TO_BUCKET"')
    exit(1)

# Get Queue Name; Fail fast if not provided
QUEUE_NAME = os.getenv('QUEUE_NAME', '')
if QUEUE_NAME == "":
    logging.fatal('Missing Environment Variable "QUEUE_NAME"')
    exit(1)

# Get Cumulus API Root; Fail fast if not provided
CUMULUS_API_ROOT = os.getenv('CUMULUS_API_ROOT', '')
if CUMULUS_API_ROOT == '':
    logging.fatal('Missing Environment Variable "CUMULUS_API_ROOT"')
    exit(1)

S3_ENDPOINT = os.getenv('S3_ENDPOINT', default=None)

def _get_s3_resource(endpoint_url=S3_ENDPOINT):

    if endpoint_url:
        s3 = boto3.resource('s3', endpoint_url=endpoint_url)
    else:
        s3 = boto3.resource('s3')


def get_infile(bucket, key, filepath):

    s3 = _get_s3_resource()

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
    And 
    """

    # Upload the file    
    s3 = _get_s3_resource()

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    try:
        response = s3.Bucket(bucket).upload_file(file_name, object_name)
    except botocore.exceptions.ClientError as e:
        logger.error('Unable to upload file to S3.')
        logger.error(e)
        return False
    return True


def get_infile_processor(name):
    """Import library for processing a given product_name"""
    
    processor = importlib.import_module(f'cumulus.processors.{name}')
    
    return processor


def get_products():

    r = requests.get(f'{CUMULUS_API_ROOT}/cumulus/v1/products')
    if r.status_code == 200:
        return { item['name']: item["id"] for item in r.json() }
    return None


def handle_message(msg):
    """Converts JSON-Formatted message string to dictionary and calls package()"""
    print(msg)
    print(type(msg))
    msg_body = json.loads(msg.body)
    print(msg_body)
    return msg_body

    # bucket, key = msg_body['s3_bucket'], unquote_plus(msg_body['s3_key'])

    # # # Filename and product_name
    # pathparts = key.split('/')
    # acquirable_name, filename = pathparts[1], pathparts[-1]
    # logger.info(f'Process acquirable_name: {acquirable_name}; file: {filename}')

    # # Find library to unleash on file
    # processor = get_infile_processor(acquirable_name)
    # logger.info(f'Using processor: {processor}')
       
    # with tempfile.TemporaryDirectory() as td:
        
    #     _file = get_infile(bucket, key, os.path.join(td, filename))
    #     print(_file)
    #     # Process the file and return a list of files
    #     outfiles = processor.process(_file, td)
    #     logger.debug(f'outfiles: {outfiles}')
        
    #     # Keep track of successes to send as single database query at the end
    #     successes = []
    #     # Valid products in the database
    #     product_map = get_products()
    #     for _f in outfiles:
    #         # See that we have a valid 
    #         if _f["filetype"] in product_map.keys():
    #             # Write output files to different bucket
    #             write_key = 'cumulus/{}/{}'.format(_f["filetype"], _f["file"].split("/")[-1])
                
    #             upload_success = upload_file(_f["file"], WRITE_TO_BUCKET, write_key)
    #             # Write Productfile Entry to Database
    #             if upload_success:
    #                 successes.append({
    #                     "product_id": product_map[_f["filetype"]],
    #                     "datetime": _f['datetime'],
    #                     "file": write_key,
    #                 })
            
                # count = write_database(successes)
        
    # return {}
        # "count": len(successes),
        # "productfiles": successes
    


if __name__ == "__main__":


    CLIENT = boto3.resource(
        'sqs',
        endpoint_url=os.getenv('SQS_ENDPOINT_URL', default='http://elasticmq:9324'),
        region_name=os.getenv('AWS_REGION', default='elasticmq'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY', default='x'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID', default='x'),
        use_ssl=os.getenv('USE_SSL', default=False)
    )

    # Incoming Requests for Packager
    queue = CLIENT.get_queue_by_name(QueueName=QUEUE_NAME)
    print(f'queue; geoprocess       : {queue}')


    while 1:
        messages = queue.receive_messages(
            WaitTimeSeconds=int(os.getenv('WAIT_TIME_SECONDS', default=20))
        )
        print(f'packager message count: {len(messages)}')
        
        for message in messages:
            handle_message(message)
            message.delete()
