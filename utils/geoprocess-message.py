import json

from datetime import datetime, timezone

import boto3
import botocore
import botocore.exceptions


SNODAS_INCOMING_FILE_TO_COGS = {
    "geoprocess": "incoming-file-to-cogs",
    "geoprocess_config": {
        "bucket": "cwbi-data-develop",
        "key": "cumulus/nohrsc-snodas-unmasked/SNODAS_unmasked_20140101.tar"
    }
}

# https://stackoverflow.com/questions/28498163/how-do-i-construct-a-utc-datetime-object-in-python
# SAMPLE MESSAGE FOR SNODAS INTERPOLATE; DATE ONLY NEEDS TO BE ACCURATE TO THE DAY
SNODAS_INTERPOLATE_MESSAGE = {
    "geoprocess": "snodas-interpolate",
    "geoprocess_config": {
        "datetime": datetime(2014, 1, 1, tzinfo=timezone.utc).strftime("%Y%m%d"),
        "max_distance": 16,
    }
}

INCOMING_FILE_TO_COGS_MESSAGE = {
    "geoprocess": "incoming-file-to-cogs",
    "geoprocess_config": {
        "bucket": "cwbi-data-develop",
        "key": "cumulus/acquirables/ndfd-conus-temp-4to7/ds.temp47.bin"
    }
}

CLIENT = boto3.resource(
    'sqs',
    endpoint_url="http://localhost:9324",
    region_name="elasticmq",
    aws_secret_access_key="x",
    aws_access_key_id="x",
    use_ssl=False
)

# Incoming Requests
queue = CLIENT.get_queue_by_name(QueueName="cumulus-geoprocess")

print(f'queue;       : {queue}')

msg = INCOMING_FILE_TO_COGS_MESSAGE
# msg = SNODAS_INCOMING_FILE_TO_COGS
# msg = SNODAS_INTERPOLATE_MESSAGE

response = queue.send_message(MessageBody=json.dumps(msg, separators=(',', ':')))

