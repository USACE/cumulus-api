import json
import os
import numpy as np
import numpy.ma as ma
from osgeo import gdal
from affine import Affine
from collections import namedtuple

import config as CONFIG

from pydsstools.heclib.dss.HecDss import Open
from pydsstools.heclib.utils import gridInfo


def write_contents_to_dssfile(outfile, watershed, items, callback, cellsize=2000, dst_srs="EPSG:5070"):

    HEC_WKT = '"PROJCS[\"USA_Contiguous_Albers_Equal_Area_Conic_USGS_version\",GEOGCS[\"GCS_North_American_1983\",DATUM[\"D_North_American_1983\",SPHEROID[\"GRS_1980\",6378137.0,298.257222101]],PRIMEM[\"Greenwich\",0.0],UNIT[\"Degree\",0.0174532925199433]],PROJECTION[\"Albers\"],PARAMETER[\"False_Easting\",0.0],PARAMETER[\"False_Northing\",0.0],PARAMETER[\"Central_Meridian\",-96.0],PARAMETER[\"Standard_Parallel_1\",29.5],PARAMETER[\"Standard_Parallel_2\",45.5],PARAMETER[\"Latitude_Of_Origin\",23.0],UNIT[\"Meter\",1.0]]"'

    with Open(outfile) as fid:

        item_length = len(items)

        Watershed = namedtuple("Watershed", watershed)
        _watershed = Watershed(**watershed)

        for idx, item in enumerate(items):
            # Update progress at predefined interval
            if idx % CONFIG.PACKAGER_UPDATE_INTERVAL == 0 or idx == item_length-1:
                callback(idx)

            # Named tuple for the watershed's contents
            WatershedContent = namedtuple("WatershedContent", item)
            content = WatershedContent(**item)

            try:

                ds = gdal.Warp(
                    '/vsimem/projected.tif',
                    f'/vsis3_streaming/{content.bucket}/{content.key}',
                    dstSRS=dst_srs,
                    outputType=gdal.GDT_Float64,
                    outputBounds=_watershed.bbox,
                    resampleAlg="bilinear",
                    targetAlignedPixels=True,
                    xRes=cellsize,
                    yRes=cellsize,
                )

                # Raw Cell Values as Array
                data = ds.GetRasterBand(1).ReadAsArray().astype(np.dtype('float32'))

                # Get the grid info and its noDataValue
                fileinfo = gdal.Info(f'/vsis3_streaming/{content.bucket}/{content.key}', format='json')
                try:
                    if isinstance(nodatavalue := fileinfo['bands'][0]['noDataValue'], (int, float)):
                        data = np.where((data == nodatavalue), np.nan, data)
                except KeyError as err:
                    print(err)

                # Projection
                proj = HEC_WKT if ("5070" in dst_srs) else ds.GetProjection()

                # Affine Transform
                geo_transform = ds.GetGeoTransform()

                affine_transform = Affine(cellsize,0,0,0,0,0) if ("5070" in dst_srs) \
                    else Affine.from_gdal(*geo_transform)

                # Create HEC GridInfo Object
                grid_info = gridInfo()
                grid_info.update([
                    ('grid_type','shg-time'),
                    ('grid_crs', proj),
                    ('grid_transform', affine_transform),
                    ('data_type', content.dss_datatype.lower()),
                    ('data_units', content.dss_unit.lower()),
                    ('opt_crs_name', 'AlbersInfo'),
                    ('opt_lower_left_x', _watershed.bbox[0] / cellsize),
                    ('opt_lower_left_y', _watershed.bbox[1] / cellsize),
                ])
                    # ('opt_is_interval', True),
                    # ('opt_time_stamped', True),
                fid.put_grid(
                    f'/SHG/{_watershed.name}/{content.dss_cpart}/{content.dss_dpart}/{content.dss_epart}/{content.dss_fpart}/',
                    data,
                    grid_info
                )
        
            except:
                print(f'Unable to process: {content.bucket}/{content.key}')

            finally:
                ds = None
                data = None

    return os.path.abspath(outfile)