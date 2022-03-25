"""Initialize geoprocess worker with needed env vars

Also setup logger
"""

import os
import logging
from signal import SIGINT, SIGTERM, signal


# ------------------------- #
# setup the logging for the package
# ------------------------- #
logger = logging.getLogger(__package__)
LOGGER_LEVEL = os.getenv("LOGGER_LEVEL", default="WARNING")
log_level = logging._nameToLevel[LOGGER_LEVEL]
logger.setLevel(log_level)

formatter = logging.Formatter(
    "[%(asctime)s.%(msecs)03d] "
    + "{%(name)20s:%(funcName)20s} - %(levelname)-7s - %(message)s",
    "%Y-%m-%dT%H:%M:%S",
)

ch = logging.StreamHandler()

ch.setFormatter(formatter)
logger.addHandler(ch)


# ------------------------- #
# Signal Handler
# ------------------------- #
class SignalHandler:
    def __init__(self):
        self.received_signal = False
        signal(SIGINT, self._signal_handler)
        signal(SIGTERM, self._signal_handler)

    def _signal_handler(self, signal, frame):
        print(f"handling signal {signal}, exiting gracefully")
        self.received_signal = True


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
