import json
import boto3

CLIENT = boto3.resource(
    "sqs",
    endpoint_url="http://localhost:9324",
    region_name="elasticmq",
    aws_secret_access_key="x",
    aws_access_key_id="x",
    use_ssl=False,
)

# Incoming Requests
CLIENT.get_queue_by_name(
    QueueName="cumulus-statistics"
).send_message(
    MessageBody=json.dumps(
        {
            "geometry_info": {
                "url": "https://develop-water-api.corps.cloud/watersheds/guyandotte-river/geometry",
            },
            "raster_info": {
                "bucket": "castle-data-develop",
                "key": "MRMS_MultiSensor_QPE_01H_Pass1_00.00_20220718-170000.tif",
            },
            "analysis_info": {
                "srs": "EPSG:5070",
                "cellsize": 1000,
                "coordinate_precision": 0,
                "statistic_precision": 2
            },
            "output_info": {
                "url": "https://mimir.corps.cloud/v1/write"
            }
        },
        separators=(",", ":")
    )
)
