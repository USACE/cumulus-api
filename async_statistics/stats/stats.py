import logging
import os
import json
from time import sleep
import tempfile
from uuid import uuid4
import shutil

from osgeo import gdal
import boto3
from rasterstats import zonal_stats

import config as CONFIG
from helpers import buffered_extent
from db import get_basin

CLIENT = boto3.resource(
    'sqs',
    endpoint_url=CONFIG.ENDPOINT_URL,
    region_name=CONFIG.REGION_NAME,
    aws_secret_access_key=CONFIG.AWS_SECRET_ACCESS_KEY,
    aws_access_key_id=CONFIG.AWS_ACCESS_KEY_ID,
    use_ssl=CONFIG.USE_SSL
)

# Incoming Requests for Statistics
queue_statistics = CLIENT.get_queue_by_name(QueueName=CONFIG.QUEUE_NAME_STATISTICS)
print(f'queue; statistics       : {queue_statistics}')

# Logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

# Packager Update Function
def statistics(item):
    """Item: { bucket: "", key: "", }"""

    cellsize = 2000
    # minx, miny, maxx, maxy = buffered_extent(
    #     [-1394000, 1552000, 510000, 3044000], 2, cellsize
    # )
    with tempfile.TemporaryDirectory(prefix=uuid4().__str__()) as td:

        projected_raster = os.path.abspath(os.path.join(td, 'projected.tif'))

        # TODO: Add outputBounds on warp using buffered basin extent
        # this should significantly speed up statistics by avoiding a resample and download
        # of the entire grid extent.
        ds = gdal.Warp(
            projected_raster,
            f'/vsis3_streaming/{item["s3_bucket"]}/{item["s3_key"]}',
            dstSRS='EPSG:5070',
            outputType=gdal.GDT_Float64,
            resampleAlg="bilinear",
            targetAlignedPixels=True,
            xRes=cellsize,
            yRes=cellsize
        )
        ds = None
        
        geometry = get_basin(item["basin_id"])
        
        features = zonal_stats(
            [geometry[0]], projected_raster, stats=["min", "max", "mean", "count", ], geojson_out=True
        )

        result = [
            {
                "productfile_id": item['productfile_id'],
                "basin_id": item['basin_id'],
                "min": f['properties']['min'],
                "max": f['properties']['max'],
                "mean": f['properties']['mean']
            } for f in features
        ]

    return json.dumps(result, indent=2)


def handle_message(msg):
    """Converts JSON-Formatted message string to dictionary and calls package()"""

    print('\n\nmessage received\n\n')
    j = json.loads(msg.body)
    result = statistics(j)
    print(result)


while 1:
    messages = queue_statistics.receive_messages(WaitTimeSeconds=CONFIG.WAIT_TIME_SECONDS)
    print(f'message count: {len(messages)}')
    
    for message in messages:
        handle_message(message)
        message.delete()
