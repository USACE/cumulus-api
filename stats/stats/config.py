import os

ENDPOINT_URL_S3 = os.getenv('ENDPOINT_URL_S3', default='http://elasticmq:9324')
ENDPOINT_URL_SQS = os.getenv('ENDPOINT_URL_SQS', default='http://elasticmq:9324')
# 
# AWS Credentials
# 
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', default='x')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', default='x')
AWS_DEFAULT_REGION = os.getenv('AWS_DEFAULT_REGION', default='us-east-1')
AWS_REGION_SQS = os.getenv("AWS_REGION_SQS", default=None)
# 
# Configuration Parameters
# 
# Use SSL setting to 'True' as default if env var unset from docker-compose
# client and resource use_ssl default=True; ignored is endpoint_url defined
USE_SSL: bool = eval(os.getenv("USE_SSL", default="True").title())
# ------------------------- #
# SQS Configuration
# ------------------------- #
QUEUE_NAME: str = os.getenv("QUEUE_NAME", "cumulus-geoprocess")
WAIT_TIME_SECONDS: int = os.getenv("WAIT_TIME_SECONDS", default=20)
MAX_Q_MESSAGES: int = os.getenv("MAX_Q_MESSAGES", default=10)
