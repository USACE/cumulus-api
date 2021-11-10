import os
import logging
logger = logging.getLogger(__name__)

LOGLEVEL = logging.DEBUG
APPLICATION_KEY = os.getenv("APPLICATION_KEY", default="appkey")
CUMULUS_API_URL = os.getenv('CUMULUS_API_URL', default='http://api:80')

#################
# AWS Credentials
#################
AWS_REGION = os.getenv('AWS_REGION', default='us-east-1')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', default='x')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', default='x')

###################
# SQS CONFIGURATION
###################
AWS_REGION_SQS = os.getenv('AWS_REGION_SQS', default=AWS_REGION)
ENDPOINT_URL_SQS = os.getenv('ENDPOINT_URL_SQS', default='http://elasticmq:9324')
QUEUE_NAME=os.getenv('QUEUE_NAME', 'cumulus-geoprocess')

##################
# S3 CONFIGURATION
##################
AWS_REGION_S3 = os.getenv('AWS_REGION_S3', default=AWS_REGION)
ENDPOINT_URL_S3 = os.getenv('ENDPOINT_URL_S3', default=None)
WRITE_TO_BUCKET = os.getenv('WRITE_TO_BUCKET', default='castle-data-develop')

##########################
# Configuration Parameters
##########################

# MOCK File Uploads to S3 (i.e. print) or actually upload
if os.getenv('CUMULUS_MOCK_S3_UPLOAD', default="False").upper() == "TRUE":
    CUMULUS_MOCK_S3_UPLOAD = True
else:
    # If CUMULUS_MOCK_S3_UPLOAD environment variable is unset then CUMULUS_MOCK_S3_UPLOAD will equal False
    CUMULUS_MOCK_S3_UPLOAD = False

# Use SSL
if os.getenv('USE_SSL', default="True").upper() == "FALSE":
    USE_SSL = False
else:
    USE_SSL = True


WAIT_TIME_SECONDS = os.getenv('WAIT_TIME_SECONDS', default=20)
