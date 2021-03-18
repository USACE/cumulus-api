import os
import logging
logger = logging.getLogger(__name__)

LOGLEVEL = logging.DEBUG

# 
# AWS Credentials
# 
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', default=None)
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', default=None)
AWS_REGION = os.getenv('AWS_REGION', default='us-east-1')

# If _SQS versions of AWS_SECRET_ACCESS_KEY, AWS_ACCESS_KEY_ID, AWS_REGION not explicitly set,
# set to usual environment variables for AWS credentials. Variables with _SQS suffix are intended
# to be used when override is required for elasticmq (variables set to 'x' or 'elasticmq') for local testing.
# See Documentation Here: https://github.com/softwaremill/elasticmq#using-the-amazon-boto-python-to-access-an-elasticmq-server
AWS_SECRET_ACCESS_KEY_SQS = os.getenv('AWS_SECRET_ACCESS_KEY_SQS', default=AWS_SECRET_ACCESS_KEY)
AWS_ACCESS_KEY_ID_SQS = os.getenv('AWS_ACCESS_KEY_ID_SQS', default=AWS_ACCESS_KEY_ID)
AWS_REGION_SQS = os.getenv('AWS_REGION_SQS', default=AWS_REGION)


# S3
ENDPOINT_URL_S3 = os.getenv('ENDPOINT_URL_S3', default=None)
WRITE_TO_BUCKET = 'corpsmap-data'

# MOCK File Uploads to S3 (i.e. print) or actually upload
if os.getenv('CUMULUS_MOCK_S3_UPLOAD', default="False").upper() == "TRUE":
    CUMULUS_MOCK_S3_UPLOAD = True
else:
    # If CUMULUS_MOCK_S3_UPLOAD environment variable is unset then CUMULUS_MOCK_S3_UPLOAD will equal False
    CUMULUS_MOCK_S3_UPLOAD = False


ENDPOINT_URL_SQS = os.getenv('ENDPOINT_URL_SQS', default='http://elasticmq:9324')
QUEUE_NAME=os.getenv('QUEUE_NAME', 'cumulus-geoprocess')

# 
# Database Credentials
# 
CUMULUS_DBUSER = os.getenv('CUMULUS_DBUSER', default='postgres')
CUMULUS_DBHOST = os.getenv('CUMULUS_DBHOST', default='cumulusdb')
CUMULUS_DBNAME = os.getenv('CUMULUS_DBNAME', default='postgres')
CUMULUS_DBPASS = os.getenv('CUMULUS_DBPASS', default='postgres')

# 
# Configuration Parameters
# 
USE_SSL = os.getenv('USE_SSL', default=False)

WAIT_TIME_SECONDS = os.getenv('WAIT_TIME_SECONDS', default=20)

CUMULUS_API_URL = os.getenv('CUMULUS_API_URL', default='http://api:80')
CUMULUS_API_HOST_HEADER = os.getenv('CUMULUS_API_HOST_HEADER', default=None)