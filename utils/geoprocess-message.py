import json

from datetime import datetime, timezone

import boto3
import botocore
import botocore.exceptions

SNODAS_INCOMING_FILE_TO_COGS = {
    "geoprocess": "incoming-file-to-cogs",
    "geoprocess_config": {
        "bucket": "cwbi-data-develop",
        "key": "cumulus/nohrsc-snodas-unmasked/SNODAS_unmasked_20140101.tar",
    },
}

# https://stackoverflow.com/questions/28498163/how-do-i-construct-a-utc-datetime-object-in-python
# SAMPLE MESSAGE FOR SNODAS INTERPOLATE; DATE ONLY NEEDS TO BE ACCURATE TO THE DAY
SNODAS_INTERPOLATE_MESSAGE = {
    "geoprocess": "snodas-interpolate",
    "geoprocess_config": {
        "datetime": datetime(2014, 1, 1, tzinfo=timezone.utc).strftime("%Y%m%d"),
        "max_distance": 16,
    },
}

INCOMING_FILE_TO_COGS_MESSAGE = {
    "geoprocess": "incoming-file-to-cogs",
    "geoprocess_config": {
        "acquirablefile_id": "11a69c52-3a59-4c50-81a6-eba26e6573d4",
        "acquirable_id": "2429db9a-9872-488a-b7e3-de37afc52ca4",
        "acquirable_slug": "cbrfc-mpe",
        "bucket": "castle-data-develop",
        "key": "cumulus/acquirables/ncep-mrms-v12-multisensor-qpe-01h-pass1/MRMS_MultiSensor_QPE_01H_Pass1_00.00_20211113-160000.grib2.gz",
    },
}


{
    "geoprocess": "incoming-file-to-cogs",
    "geoprocess_config": {
        "bucket": "cwbi-data-develop",
        "key": f"cumulus/acquirables/nbm-co-01h/blend.20211109.t20z.core.f030.co.grib2",
    },
}

CLIENT = boto3.resource(
    "sqs",
    endpoint_url="http://localhost:9324",
    region_name="elasticmq",
    aws_secret_access_key="x",
    aws_access_key_id="x",
    use_ssl=False,
)

# Incoming Requests
queue = CLIENT.get_queue_by_name(QueueName="cumulus-geoprocess")

print(f"queue;       : {queue}")

msg = INCOMING_FILE_TO_COGS_MESSAGE
# msg = SNODAS_INCOMING_FILE_TO_COGS
# msg = SNODAS_INTERPOLATE_MESSAGE

response = queue.send_message(MessageBody=json.dumps(msg, separators=(",", ":")))
