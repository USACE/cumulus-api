import os

ENDPOINT_URL = os.getenv('ENDPOINT_URL', default='http://elasticmq:9324')
QUEUE_NAME_STATISTICS=os.getenv('QUEUE_NAME_STATISTICS', 'cumulus-statistics')

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
USE_SSL = os.getenv('USE_SSL', default=False)

WAIT_TIME_SECONDS = os.getenv('WAIT_TIME_SECONDS', default=20)

CUMULUS_API_URL = os.getenv('CUMULUS_API_URL', default='http://api:3030')