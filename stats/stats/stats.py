import asyncio
import logging
import os
import json
import tempfile
from uuid import uuid4

from osgeo import gdal
import httpx
import boto3
from rasterstats import zonal_stats, point_query

from config import (
    AWS_SECRET_ACCESS_KEY,
    AWS_ACCESS_KEY_ID,
    ENDPOINT_URL_SQS,
    QUEUE_NAME,
    AWS_REGION_SQS,
    USE_SSL,
    MAX_Q_MESSAGES,
    WAIT_TIME_SECONDS
)

# Logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


async def get_geometry(url: str):
    """Expects geojson-formatted geometry returned from url"""
    async with httpx.AsyncClient(http2=True) as client:
        resp = await client.get(url)
        if resp.status_code == 200:
            return resp.json()
    return None


def output_to_target(payload: str, output_info: dict):
    print("##############################################")
    print(f"TODO;; MOCK_WRITE_TO_TARGET: {output_info}")
    print(f'payload:\n{json.dumps(payload, indent=2)}')
    print("##############################################")
    return True


def statistics(geometry, raster, srs='EPSG:4326', cellsize=.01):

    def format_statistics(features):
        """Format statistics returned by rasterstats.zonal_stats()"""

        return [ _f['properties'] for _f in features ]
     
    """Item: { s3_bucket: "", s3_key: "", }"""

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
            raster,
            dstSRS=srs,
            outputType=gdal.GDT_Float64,
            resampleAlg="bilinear",
            targetAlignedPixels=False,
            xRes=cellsize,
            yRes=cellsize,
            outputBounds=geometry["bbox"]
        )
        ds = None
        
        # Compute Statistics
        features = zonal_stats(
            geometry['geometry'], projected_raster, geojson_out=True,
        )

    return format_statistics(features)


def handle_message(msg):
    """Converts JSON-Formatted message string to dictionary and calls package()"""

    STATUS_SUCCEEDED, STATUS_FAILED = 'succeeded', 'failed'

    j = json.loads(msg.body)

    # Status Message for Monitoring
    # Status is "succeded" or "failed"
    outcome_message = { 'raster': None, 'geometry': None, 'status': None, 'error_message': None }

    # Raster
    r = f'/vsis3_streaming/{j["raster_info"]["bucket"]}/{j["raster_info"]["key"]}'
    outcome_message['raster'] = r

    # Geometry
    geom_url = j['geometry_info']['url']
    outcome_message['geometry'] = geom_url
    # Fetch GeoJSON Geometry
    g = asyncio.run(get_geometry(geom_url))
    if g is None:
        outcome_message['status'] = STATUS_FAILED
        outcome_message['error_message'] = "get_geometry() failed"
        return outcome_message
    else:
        outcome_message['geometry'] = geom_url
    
    # Run Statistics
    stats = statistics(g, r)
    if stats is None:
        outcome_message['status'] = STATUS_FAILED
        outcome_message['error_message'] = "statistics() failed"
        return outcome_message
    
    # Output to Target
    # TODO: Implement correct payload
    output_info = j['output_info']
    payload = {
        'stats': stats,
    }
    store_went_ok = output_to_target(payload, output_info)
    if not store_went_ok:
        outcome_message['status'] = STATUS_FAILED
        outcome_message['error_message'] = "output results failed"
        return outcome_message
    
    outcome_message['status'] = STATUS_SUCCEEDED

    return outcome_message


if __name__ == "__main__":

    # SAMPLE MESSAGE
    # {
    #     "geometry_url": "https://water-api.corps.cloud/watersheds/upper-mississippi-river/geometry",
    #     "raster_info": {
    #         "bucket": "s3://my-bucket",
    #         "key": "abc/123/mytif.tif"
    #     },
    #     "output_url": "https://mimir.corps.cloud/v1/write",
    # }

    CLIENT = boto3.resource(
        'sqs',
        endpoint_url=ENDPOINT_URL_SQS,
        region_name=AWS_REGION_SQS,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        use_ssl=USE_SSL
    )

    # Incoming Requests for Statistics
    queue_statistics = CLIENT.get_queue_by_name(QueueName=QUEUE_NAME)
    print(f'queue; statistics       : {queue_statistics}')

    while 1:
        
        messages = queue_statistics.receive_messages(
            WaitTimeSeconds=WAIT_TIME_SECONDS,
            MaxNumberOfMessages=MAX_Q_MESSAGES
        )

        print(f'message count: {len(messages)}')

        for message in messages:
            outcome_message = handle_message(message)
            print(f'outcome: {json.dumps(outcome_message)}')
            message.delete()