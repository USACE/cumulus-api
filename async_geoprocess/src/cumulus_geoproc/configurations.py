"""Initialize package with configuations
"""


import os

# ------------------------- #
# Container env vars
# ------------------------- #
APPLICATION_KEY = os.getenv("APPLICATION_KEY", default="appkey")
CUMULUS_API_URL = os.getenv("CUMULUS_API_URL", default="http://api:80")

# ------------------------- #
# AWS Credentials/Configuration
# ------------------------- #
AWS_DEFAULT_REGION = os.getenv("AWS_REGION", default="us-east-1")
AWS_REGION_SQS = os.getenv("AWS_REGION_SQS", default="elasticmq")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", default=None)
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", default=None)
AWS_VIRTUAL_HOSTING = os.getenv("AWS_VIRTUAL_HOSTING", default="FALSE")
AWS_HTTPS = os.getenv("AWS_HTTPS", default="YES")
ENDPOINT_URL_SQS = os.getenv("ENDPOINT_URL_SQS", default="http://elasticmq:9324")
ENDPOINT_URL_S3 = os.getenv("ENDPOINT_URL_S3", default=None)

# Use SSL setting to 'True' as default if env var unset from docker-compose
# client and resource use_ssl default=True; ignored is endpoint_url defined
USE_SSL = eval(os.getenv("USE_SSL", default="True").title())
# ------------------------- #
# SQS Configuration
# ------------------------- #
QUEUE_NAME = os.getenv("QUEUE_NAME", "cumulus-geoprocess")
WAIT_TIME_SECONDS = os.getenv("WAIT_TIME_SECONDS", default=20)
MAX_Q_MESSAGES = os.getenv("MAX_Q_MESSAGES", default=10)

# ------------------------- #
# S3 Configuration
# ------------------------- #
WRITE_TO_BUCKET = os.getenv("WRITE_TO_BUCKET", default="castle-data-develop")


# ------------------------- #
# GDAL Configuration
# ------------------------- #
GDAL_DISABLE_READDIR_ON_OPEN = os.getenv("GDAL_DISABLE_READDIR_ON_OPEN", default="YES")
CPL_VSIL_USE_TEMP_FILE_FOR_RANDOM_WRITE = os.getenv(
    "CPL_VSIL_USE_TEMP_FILE_FOR_RANDOM_WRITE", default="YES"
)
CPL_TMPDIR = os.getenv("CPL_TMPDIR", default="/tmp")


# ------------------------- #
# Configuration Parameters
# ------------------------- #

# MOCK File Uploads to S3 (i.e. print) or actually upload

# Set to env var from docker-compose and default to 'False' is unset
CUMULUS_MOCK_S3_UPLOAD = eval(
    os.getenv("CUMULUS_MOCK_S3_UPLOAD", default="False").title()
)


# HTTP protocol used in httpx
HTTP2 = eval(os.getenv("HTTP2", default="True").title())

# Cumulus products key
CUMULUS_PRODUCTS_BASEKEY = os.getenv(
    "CUMULUS_PRODUCTS_BASEKEY", default="cumulus/products"
)

# Resulting product file version default
PRODUCT_FILE_VERSION = os.getenv(
    "PRODUCT_FILE_VERSION", default="1111-11-11T11:11:11.11Z"
)

LOGGER_LEVEL = os.getenv("LOGGER_LEVEL", default="WARNING")


# ~~~~~~~~~~~~~~~~~~~~~~


# ------------------------- #
# Container env vars
# ------------------------- #
APPLICATION_KEY = os.getenv("APPLICATION_KEY", default="appkey")
CUMULUS_API_URL = os.getenv("CUMULUS_API_URL", default="http://api:80")

# ------------------------- #
# AWS Credentials
# ------------------------- #
AWS_REGION = os.getenv("AWS_REGION", default="us-east-1")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", default=None)
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", default=None)

# ------------------------- ###
# SQS CONFIGURATION
# ------------------------- ###
AWS_REGION_SQS = os.getenv("AWS_REGION_SQS", default=AWS_REGION)
ENDPOINT_URL_SQS = os.getenv("ENDPOINT_URL_SQS", default="http://elasticmq:9324")
QUEUE_NAME = os.getenv("QUEUE_NAME", "cumulus-geoprocess")
WAIT_TIME_SECONDS = os.getenv("WAIT_TIME_SECONDS", default=20)
MAX_Q_MESSAGES = os.getenv("MAX_Q_MESSAGES", default=10)

# ------------------------- ##
# S3 CONFIGURATION
# ------------------------- ##
AWS_REGION_S3 = os.getenv("AWS_REGION_S3", default=AWS_REGION)
ENDPOINT_URL_S3 = os.getenv("ENDPOINT_URL_S3", default=None)
WRITE_TO_BUCKET = os.getenv("WRITE_TO_BUCKET", default="castle-data-develop")

# ------------------------- #
# Configuration Parameters
# ------------------------- #

# MOCK File Uploads to S3 (i.e. print) or actually upload

# Set to env var from docker-compose and default to 'False' is unset
CUMULUS_MOCK_S3_UPLOAD = eval(
    os.getenv("CUMULUS_MOCK_S3_UPLOAD", default="False").title()
)

# Use SSL setting to 'True' as default if env var unset from docker-compose
USE_SSL = eval(os.getenv("USE_SSL", default="True").title())
