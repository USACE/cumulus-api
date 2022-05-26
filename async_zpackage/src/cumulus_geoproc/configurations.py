"""Initialize package with configuations
"""


import os

# ------------------------- #
# Container env vars
# ------------------------- #
APPLICATION_KEY: str = os.getenv("APPLICATION_KEY", default="appkey")
CUMULUS_API_URL: str = os.getenv("CUMULUS_API_URL", default="http://api:80")

# ------------------------- #
# AWS Credentials/Configuration
# ------------------------- #
AWS_DEFAULT_REGION: str = os.getenv("AWS_REGION", default="us-east-1")
AWS_REGION_SQS: str = os.getenv("AWS_REGION_SQS", default="elasticmq")
AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", default=None)
AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", default=None)
AWS_VIRTUAL_HOSTING: str = os.getenv("AWS_VIRTUAL_HOSTING", default="FALSE")
AWS_HTTPS: str = os.getenv("AWS_HTTPS", default="YES")
ENDPOINT_URL_SQS: str = os.getenv("ENDPOINT_URL_SQS", default=None)
ENDPOINT_URL_S3: str = os.getenv("ENDPOINT_URL_S3", default=None)
AWS_SQS_ENDPOINT: str = os.getenv("elasticmq:9324", default=None)
AWS_S3_ENDPOINT: str = os.getenv("minio:9000", default=None)

# Use SSL setting to 'True' as default if env var unset from docker-compose
# client and resource use_ssl default=True; ignored is endpoint_url defined
USE_SSL: bool = eval(os.getenv("USE_SSL", default="True").title())
# ------------------------- #
# SQS Configuration
# ------------------------- #
QUEUE_NAME: str = os.getenv("QUEUE_NAME", "cumulus-geoprocess")
WAIT_TIME_SECONDS: int = os.getenv("WAIT_TIME_SECONDS", default=20)
MAX_Q_MESSAGES: int = os.getenv("MAX_Q_MESSAGES", default=10)

# ------------------------- #
# S3 Configuration
# ------------------------- #
WRITE_TO_BUCKET: str = os.getenv("WRITE_TO_BUCKET", default="castle-data-develop")


# ------------------------- #
# GDAL Configuration
# ------------------------- #
GDAL_DISABLE_READDIR_ON_OPEN: str = os.getenv(
    "GDAL_DISABLE_READDIR_ON_OPEN", default="YES"
)
CPL_VSIL_USE_TEMP_FILE_FOR_RANDOM_WRITE: str = os.getenv(
    "CPL_VSIL_USE_TEMP_FILE_FOR_RANDOM_WRITE", default="YES"
)
CPL_TMPDIR: str = os.getenv("CPL_TMPDIR", default="/tmp")


# ------------------------- #
# Configuration Parameters
# ------------------------- #

# MOCK File Uploads to S3 (i.e. print) or actually upload

# Set to env var from docker-compose and default to 'False' is unset
CUMULUS_MOCK_S3_UPLOAD: bool = eval(
    os.getenv("CUMULUS_MOCK_S3_UPLOAD", default="False").title()
)


# HTTP protocol used in httpx
HTTP2: bool = eval(os.getenv("HTTP2", default="False").title())

# Cumulus products key
CUMULUS_PRODUCTS_BASEKEY: str = os.getenv(
    "CUMULUS_PRODUCTS_BASEKEY", default="cumulus/products"
)

# Resulting product file version default
PRODUCT_FILE_VERSION: str = os.getenv(
    "PRODUCT_FILE_VERSION", default="1111-11-11T11:11:11.11Z"
)

LOGGER_LEVEL: str = os.getenv("LOGGER_LEVEL", default="INFO")
