import os

# 
# AWS Credentials
# 
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', default='x')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', default='x')
REGION_NAME = os.getenv('AWS_REGION', default='elasticmq')

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
ENDPOINT_URL = os.getenv('ENDPOINT_URL', default='http://elasticmq:9324')

USE_SSL = os.getenv('USE_SSL', default=False)

WAIT_TIME_SECONDS = os.getenv('WAIT_TIME_SECONDS', default=20)

WRITE_TO_BUCKET = 'corpsmap-data'

# MOCK File Uploads to S3 (i.e. print) or actually upload
if os.getenv('CUMULUS_MOCK_S3_UPLOAD', default="False").upper() == "TRUE":
    CUMULUS_MOCK_S3_UPLOAD = True
else:
    # If CUMULUS_MOCK_S3_UPLOAD environment variable is unset then CUMULUS_MOCK_S3_UPLOAD will equal False
    CUMULUS_MOCK_S3_UPLOAD = False

CUMULUS_API_URL = os.getenv('CUMULUS_API_URL', default='https://api.rsgis.dev')

UPDATE_DOWNLOAD_METHOD = os.getenv('UPDATE_DOWNLOAD_METHOD', default='DB')
