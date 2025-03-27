""" """

import json
import logging
import os
from datetime import datetime
from pathlib import Path
import time

import boto3
import requests
from botocore.exceptions import ClientError

CUMULUS_STATIC_HOST = os.getenv("CUMULUS_STATIC_HOST")
CUMULUS_ACQUIRABLE_FILES = os.getenv("CUMULUS_ACQUIRABLE_FILES")
CUMULUS_ACQUIRABLES = os.getenv("CUMULUS_ACQUIRABLES")
CUMULUS_APPLICATION_KEY = os.getenv("CUMULUS_APPLICATION_KEY")

S3_ACQUIRABLE_PREFIX = os.getenv("S3_ACQUIRABLE_PREFIX")
S3_BUCKET = os.getenv("CUMULUS_AWS_S3_BUCKET")

GEOPROC = os.getenv("GEOPROC")
GEOPROC_TEST_DATA = os.getenv("GEOPROC_TEST_DATA")

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")


def get_acquirables():
    url = f"{CUMULUS_STATIC_HOST}{CUMULUS_ACQUIRABLES}"
    max_retries = 5
    wait_time = 5
    for attempt in range(max_retries):
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for bad responses (4xx or 5xx)
            return {obj["slug"]: obj["id"] for obj in response.json()}
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")  # Log the HTTP error
        except requests.exceptions.RequestException as req_err:
            print(f"Request error occurred: {req_err}")  # Log other request errors

        # Wait before retrying
        print(
            f"Retrying in {wait_time} seconds... (Attempt {attempt + 1}/{max_retries})"
        )
        time.sleep(wait_time)

        print("Max retries reached. Request failed.")


def get_products():
    for dirname, _, filenames in os.walk(GEOPROC_TEST_DATA):
        for filename in filenames:
            if filename.endswith(".json"):
                filepath = Path(dirname).joinpath(filename)
                with filepath.open("r", encoding="utf-8") as fptr:
                    objs = json.load(fptr)
                    if isinstance(objs, list):
                        for obj in objs:
                            yield obj


def upload_file(file_name, bucket, object_name=None):
    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    session = boto3.session.Session()
    s3_client = session.client(
        service_name="s3",
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )

    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True


def main():
    acquirables = get_acquirables()
    if acquirables is None:
        exit()

    for product in get_products():
        slug = product.get("plugin")
        local_source = product.get("local_source")
        key = local_source.replace("fixtures", "cumulus/acquirables")

        fqpn = Path(GEOPROC).joinpath(local_source)
        print(f"{fqpn=}")

        id = acquirables.get(slug)
        payload = {
            "datetime": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "file": key,
            "acquirable_id": id,
        }
        print(f"{payload=}")

        # upload the file
        if upload_file(fqpn.as_posix(), S3_BUCKET, key):
            print(f"Upload: {fqpn}")

            # notify
            url = f"{CUMULUS_STATIC_HOST}{CUMULUS_ACQUIRABLE_FILES}?key={CUMULUS_APPLICATION_KEY}"
            print(f"{url=}")

            headers = {"Content-Type": "application/json"}
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            # Check the response
            if 200 <= response.status_code < 300:
                print("Success:", response.json())
            else:
                print("Error:", response.status_code, response.text)


if __name__ == "__main__":
    main()
