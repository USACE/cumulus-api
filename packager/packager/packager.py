import logging
import os
import json
from time import sleep
import tempfile
import shutil

import boto3
import botocore
import botocore.exceptions

import config as CONFIG
from packager_update_functions import updateStatus_api, updateStatus_db

from dss import write_contents_to_dssfile


CLIENT = boto3.resource(
    'sqs',
    endpoint_url=CONFIG.ENDPOINT_URL,
    region_name=CONFIG.AWS_REGION_SQS,
    aws_secret_access_key=CONFIG.AWS_SECRET_ACCESS_KEY,
    aws_access_key_id=CONFIG.AWS_ACCESS_KEY_ID,
    use_ssl=CONFIG.USE_SSL
)

# Incoming Requests for Packager
queue_packager = CLIENT.get_queue_by_name(QueueName=CONFIG.QUEUE_NAME_PACKAGER)
print(f'queue; packager       : {queue_packager}')

# Where to send Packager updates
queue_packager_update = CLIENT.get_queue_by_name(QueueName=CONFIG.QUEUE_NAME_PACKAGER_UPDATE)
print(f'queue; packager_update: {queue_packager_update}')

# Logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

# Packager Update Function
if CONFIG.UPDATE_DOWNLOAD_METHOD.upper() == 'DB':
    packager_update_fn = updateStatus_db
else:
    packager_update_fn = updateStatus_api


def get_infile(bucket, key, filepath):
    
    s3 = boto3.client('s3')
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
    s3_client = boto3.client('s3')

    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except botocore.exceptions.ClientError as e:
        logger.error('Unable to upload file to S3.')
        logger.error(e)
        return False
    return True


def package(msg, packager_update_fn):

    print(json.dumps(msg, indent=2))

    STATUS = {
        'FAILED': 'a553101e-8c51-4ddd-ac2e-b011ed54389b',
        'INITIATED': '94727878-7a50-41f8-99eb-a80eb82f737a',
        'SUCCESS': '3914f0bd-2290-42b1-bc24-41479b3a846f'
    }

    # Get needed information from msg
    id = msg['download_id']
    output_bucket = msg['output_bucket']
    output_key = msg['output_key']
    contents = msg['contents']
    basin = msg['basin']

    filecount = len(contents)
    logger.info(f'filecount is: {filecount}')

    # If no files are present, notify database of failure and return from function
    if filecount == 0:            
        logger.info('Setting STATUS to FAILED')
        packager_update_fn(id, STATUS['FAILED'], 0, None)

        return json.dumps({
            "failure": "no files to process",
            "filecount": filecount
        })
    

    # I tried to avoid a callback function, but it's the best option among others
    # This allows us to move all code concerned with packaging a DSS file into a separate file
    # without:
    #   1. Putting imports or implementation details about a status update in the file that
    #      should only be concerned with DSS packaging.
    #   2. Calling dss.Open() inside of a for loop, adding file open/close overhead on each
    #      write.
    #  With this approach, the write_record_to_dssfile() method knows nothing more than that it
    #  has a function it needs to call with the iteration counter every time it adds a record to
    #  a dss file 
    def callbackFn(idx):
        """Notify the Cumulus API of status/progress"""
        progress = int((int(idx+1) / int(filecount))*100)

        if progress < 100:
            status_id = STATUS['INITIATED']
        else:
            status_id = STATUS['SUCCESS']

        packager_update_fn(id, status_id, progress)
        return


    # Get product count from event contents
    with tempfile.TemporaryDirectory() as td:
        print(f'Working in temporary directory: {td}')
        print('Output key is: {}'.format(output_key))
        outfile = write_contents_to_dssfile(
            os.path.join(td, os.path.basename(output_key)),
            basin,
            contents,
            callbackFn
        )

        

        # Upload the final output file to S3        
        if CONFIG.CUMULUS_MOCK_S3_UPLOAD:
            # Mock good upload to S3
            upload_success = True
            # Copy file to output directory in the container
            # shutil.copy2 will overwrite a file if it already exists.
            shutil.copy2(outfile, "/output/"+os.path.basename(outfile))
        else:
            upload_success = upload_file(outfile, CONFIG.WRITE_TO_BUCKET, output_key)
        
        # Call Packager Update Function one last time to add file key to database
        if upload_success:
            packager_update_fn(id, STATUS['SUCCESS'], 100, output_key)
        else:
            # Failed
            packager_update_fn(id, STATUS['FAILED'], 100)

    return json.dumps({
        "success": "SOMETHING",
    })


def handle_message(msg):
    """Converts JSON-Formatted message string to dictionary and calls package()"""

    print('\n\nmessage received\n\n')
    j = json.loads(msg.body)
    result = package(j, packager_update_fn)

    print(result)



while 1:
    messages = queue_packager.receive_messages(WaitTimeSeconds=CONFIG.WAIT_TIME_SECONDS)
    print(f'packager message count: {len(messages)}')
    
    for message in messages:
        handle_message(message)
        message.delete()
