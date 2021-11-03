import boto3
import json
import os
import shutil
import sys
from tempfile import TemporaryDirectory

import config as CONFIG
import helpers

# PROCESSORS
import p_snodas_interpolate
import p_incoming_file_to_cogs


import logging
logger = logging.getLogger(__name__)
logger.setLevel(CONFIG.LOGLEVEL)
logger.addHandler(logging.StreamHandler(sys.stdout))

if CONFIG.AWS_ACCESS_KEY_ID == 'x':
    # Running in AWS
    # Using IAM Role for Credentials
    if CONFIG.ENDPOINT_URL_SQS:
        CLIENT = boto3.resource(
            'sqs',
            endpoint_url=CONFIG.ENDPOINT_URL_SQS
        )
    else:
        CLIENT = boto3.resource('sqs')
else:
    # Local Testing
    # ElasticMQ with Credentials via AWS_ environment variables
    CLIENT = boto3.resource(
        'sqs',
        endpoint_url=CONFIG.ENDPOINT_URL_SQS,
        region_name=CONFIG.AWS_REGION_SQS,
        aws_secret_access_key=CONFIG.AWS_SECRET_ACCESS_KEY,
        aws_access_key_id=CONFIG.AWS_ACCESS_KEY_ID,
        use_ssl=CONFIG.USE_SSL
    )

# Incoming Requests
queue = CLIENT.get_queue_by_name(QueueName=CONFIG.QUEUE_NAME)
logger.info(f'queue;       : {queue}')


def handle_message(msg):
    """Converts JSON-Formatted message string to dictionary and calls geoprocessor"""

    logger.info('\n\nmessage received\n\n')
    payload = json.loads(msg.body)
    geoprocess, geoprocess_config = payload['geoprocess'], payload['geoprocess_config']
    logger.debug(json.dumps(payload, indent=2))

    with TemporaryDirectory() as td:

        if geoprocess == 'snodas-interpolate':
            outfiles = p_snodas_interpolate.process(geoprocess_config, td)
        elif geoprocess == 'incoming-file-to-cogs':
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
                write_key = 'cumulus/products/{}/{}'.format(_f["filetype"], _f["file"].split("/")[-1])
                if CONFIG.CUMULUS_MOCK_S3_UPLOAD:
                    # Mock good upload to S3
                    upload_success = True
                    # Copy file to tmp directory on host
                    # shutil.copy2 will overwrite a file if it already exists.
                    shutil.copy2(_f["file"], "/tmp")
                else:
                    upload_success = helpers.upload_file(
                        _f["file"], CONFIG.WRITE_TO_BUCKET, write_key
                    )
                # Write Productfile Entry to Database
                if upload_success:
                    successes.append({
                        "product_id": product_map[_f["filetype"]],
                        "datetime": _f['datetime'],
                        "file": write_key,
                        "version": _f['version'] if _f['version'] is not None else '1111-11-11T11:11:11.11Z'
                    })
        
        count = helpers.write_database(successes)


    return {"count": count, "productfiles": successes}


while 1:
    messages = queue.receive_messages(WaitTimeSeconds=CONFIG.WAIT_TIME_SECONDS)
    logger.info(f'message count: {len(messages)}')
    
    for message in messages:
        logger.debug(handle_message(message))
        message.delete()
