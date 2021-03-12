import json

from datetime import datetime, timezone

import boto3
import botocore
import botocore.exceptions

# https://stackoverflow.com/questions/28498163/how-do-i-construct-a-utc-datetime-object-in-python
# SAMPLE MESSAGE FOR SNODAS INTERPOLATE; DATE ONLY NEEDS TO BE ACCURATE TO THE DAY
SNODAS_INTERPOLATE_MESSAGE = {
    "process": "snodas-interpolate",
    "process_config": {
        "datetime": datetime(2014, 4, 1, tzinfo=timezone.utc).strftime("%Y%m%d"),
        "max_distance": 16,
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

msg = SNODAS_INTERPOLATE_MESSAGE

response = queue.send_message(MessageBody=json.dumps(msg, separators=(',', ':')))


