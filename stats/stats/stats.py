import asyncio
import logging
import os
import json
import tempfile
from uuid import uuid4

from osgeo.gdal import Warp, GDT_Float64
import httpx
import boto3

from pyproj import Transformer
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


def statistics(geometry, raster, srs='EPSG:4326', cellsize=.01, statistic_precision=2, coordinate_precision=4):

    def format_statistics(features):
        """Format statistics returned by rasterstats.zonal_stats()"""

        ss = {}
        for _f in features:
            for _k, _v in _f['properties'].items():
                if _k in ('min', 'max', 'mean'):
                    ss[_k] = round(_v, statistic_precision)
                else:
                    ss[_k] = _v
        
        return ss
    

    def transform_geojson_to_srs(geometry):
        """Helper function to convert GeoJSON from EPSG:4326 to specified SRS, if necessary"""
        
        if srs.upper() != 'EPSG:4326':
            logger.info(f"Analysis Does Not Reference EPSG:4326; GeoJSON Transformation from EPSG:4326 --> {srs} with coordinate_precision: {coordinate_precision}")
            
            # Define Coordinate System Transformation
            _transformer = Transformer.from_crs("EPSG:4326", srs, always_xy=True)
            
            # Transform Geometry Coordinates
            transformed_coordinates = []
            for _ring in geometry['geometry']['coordinates']:
                # Polygons can have outer and inner rings; Polygon GeoJSON is array of array(s) of points (x,y) 
                # https://macwright.com/2015/03/23/geojson-second-bite.html#polygons
                _ring_coords = []
                for _c in _ring:
                    _c_transformed = _transformer.transform(_c[0], _c[1])
                    _ring_coords.append([round(_c_transformed[0], coordinate_precision), round(_c_transformed[1], coordinate_precision)])
                transformed_coordinates.append(_ring_coords)

            geometry['geometry']['coordinates'] = transformed_coordinates

            # Transform BBOX Coordinates; Check all corner coordinates for new max/min values
            _xmin, _ymin, _xmax, _ymax = geometry['bbox']  # Original bbox, before transformation
            # Corner Coordinates on Bounding Box; [LowerLeft, LowerRight, UpperRight, UpperLeft]
            _transformed_corners = [_transformer.transform(_p[0], _p[1]) for _p in [[_xmin, _ymin], [_xmax, _ymin], [_xmax, _ymax], [_xmin, _ymax]]]
            _xvals = [p[0] for p in _transformed_corners]
            _yvals = [p[1] for p in _transformed_corners]
            
            # Set Transformed Bounding Box
            geometry['bbox'] = [
                round(min(_xvals), coordinate_precision),
                round(min(_yvals), coordinate_precision),
                round(max(_xvals), coordinate_precision),
                round(max(_yvals), coordinate_precision)
            ]

        return geometry
    

    with tempfile.TemporaryDirectory(prefix=uuid4().__str__()) as td:

        projected_raster = os.path.abspath(os.path.join(td, 'projected.tif'))

        # Transforms Geometry to SRS, if necessary. Geometry is unaltered if srs='EPSG:4326'
        geometry = transform_geojson_to_srs(geometry)

        ds = Warp(
            projected_raster,
            raster,
            dstSRS=srs,
            outputType=GDT_Float64,
            resampleAlg="bilinear",
            targetAlignedPixels=True,
            xRes=cellsize,
            yRes=cellsize,
            outputBounds=geometry["bbox"]
        )
        ds = None

        # Compute Statistics
        features = zonal_stats(geometry, projected_raster, geojson_out=True)

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

    # Get Analysis Information (Adjustments that Control How Analysis is Performed)
    # If analysis_info is not specified, set default values
    analysis_info = j['analysis_info']
    srs = analysis_info.get('srs', 'EPSG:4326')
    cellsize = analysis_info.get('cellsize', 0.01)
    statistic_precision = analysis_info.get('statistic_precision', 2)
    coordinate_precision = analysis_info.get('coordinate_precision', 4)
        
    # Run Statistics
    stats = statistics(g, r, srs=srs, cellsize=cellsize, coordinate_precision=coordinate_precision, statistic_precision=statistic_precision)
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