"""S3 operations"""
import logging
import os
import boto3
from pathlib import Path

logger = logging.getLogger(__name__)


class S3Client:
    """S3 client wrapper"""

    def __init__(self):
        self.client = boto3.client(
            's3',
            endpoint_url=os.getenv('AWS_S3_ENDPOINT'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        )

    def download_file(self, bucket: str, key: str, local_path: Path):
        """Download file from S3"""
        logger.debug(f"Downloading s3://{bucket}/{key} to {local_path}")
        self.client.download_file(bucket, key, str(local_path))

    def upload_file(self, local_path: str, bucket: str, key: str):
        """Upload file to S3"""
        logger.debug(f"Uploading {local_path} to s3://{bucket}/{key}")
        self.client.upload_file(local_path, bucket, key)
