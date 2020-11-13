import os

ENDPOINT_URL = os.getenv('ENDPOINT_URL', default='http://elasticmq:9324')
QUEUE_NAME_PACKAGER=os.getenv('QUEUE_NAME_PACKAGER', 'packager')
QUEUE_NAME_PACKAGER_UPDATE=os.getenv('QUEUE_NAME_PACKAGER_UPDATE', 'packager_update')
# How often to send status updates
PACKAGER_UPDATE_INTERVAL = int(os.getenv('PACKAGER_UPDATE_INTERVAL', default=5))

# 
# AWS Credentials
# 
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', default='x')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', default='x')
AWS_REGION = os.getenv('AWS_REGION', default='us-east-1')

AWS_SECRET_ACCESS_KEY_SQS = os.getenv('AWS_SECRET_ACCESS_KEY_SQS', default='x')
AWS_ACCESS_KEY_ID_SQS = os.getenv('AWS_ACCESS_KEY_ID_SQS', default='x')
AWS_REGION_SQS = os.getenv('AWS_REGION_SQS', default='elasticmq')

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

WRITE_TO_BUCKET = 'corpsmap-data'

# MOCK File Uploads to S3 (i.e. print) or actually upload
if os.getenv('CUMULUS_MOCK_S3_UPLOAD', default="False").upper() == "TRUE":
    CUMULUS_MOCK_S3_UPLOAD = True
else:
    # If CUMULUS_MOCK_S3_UPLOAD environment variable is unset then CUMULUS_MOCK_S3_UPLOAD will equal False
    CUMULUS_MOCK_S3_UPLOAD = False

CUMULUS_API_URL = os.getenv('CUMULUS_API_URL', default='https://api.rsgis.dev')

UPDATE_DOWNLOAD_METHOD = os.getenv('UPDATE_DOWNLOAD_METHOD', default='DB')
