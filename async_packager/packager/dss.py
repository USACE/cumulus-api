import os
import numpy as np
import numpy.ma as ma
from osgeo import gdal
from affine import Affine

import config as CONFIG

from pydsstools.heclib.dss.HecDss import Open
from pydsstools.heclib.utils import gridInfo


def write_contents_to_dssfile(outfile, watershed, items, callback):

    cellsize = 2000

    with Open(outfile) as fid:

        item_length = len(items)

        for idx, item in enumerate(items):
            # Update progress at predefined interval
            if idx % CONFIG.PACKAGER_UPDATE_INTERVAL == 0 or idx == item_length-1:
                callback(idx)

            ds = gdal.Warp(
                '/vsimem/projected.tif',
                f'/vsis3_streaming/{item["bucket"]}/{item["key"]}',
                dstSRS='EPSG:5070',
                outputType=gdal.GDT_Float64,
                outputBounds=watershed["bbox"],
                resampleAlg="bilinear",
                targetAlignedPixels=True,
                xRes=cellsize,
                yRes=cellsize
            )

            # Raw Cell Values as Array
            data = ds.GetRasterBand(1).ReadAsArray().astype(np.dtype('float32'))

            # Projection
            # proj = ds.GetProjection()
            proj = '"PROJCS[\"USA_Contiguous_Albers_Equal_Area_Conic_USGS_version\",GEOGCS[\"GCS_North_American_1983\",DATUM[\"D_North_American_1983\",SPHEROID[\"GRS_1980\",6378137.0,298.257222101]],PRIMEM[\"Greenwich\",0.0],UNIT[\"Degree\",0.0174532925199433]],PROJECTION[\"Albers\"],PARAMETER[\"False_Easting\",0.0],PARAMETER[\"False_Northing\",0.0],PARAMETER[\"Central_Meridian\",-96.0],PARAMETER[\"Standard_Parallel_1\",29.5],PARAMETER[\"Standard_Parallel_2\",45.5],PARAMETER[\"Latitude_Of_Origin\",23.0],UNIT[\"Meter\",1.0]]"'

            # Affine Transform
            geo_transform = ds.GetGeoTransform()
            affine_transform = Affine.from_gdal(*geo_transform)

            # Create HEC GridInfo Object
            grid_info = gridInfo()
            grid_info.update([
                ('grid_type','shg-time'),
                ('grid_crs', proj),
                ('grid_transform', Affine(cellsize,0,0,0,0,0)),
                ('data_type', item['dss_datatype'].lower()),
                ('data_units', item['dss_unit'].lower()),
                ('opt_crs_name', 'AlbersInfo'),
                ('opt_is_interval', True),
                ('opt_time_stamped', True),
                ('opt_lower_left_x', watershed['bbox'][0] / cellsize),
                ('opt_lower_left_y', watershed['bbox'][1] / cellsize),
            ])

            fid.put_grid(
                f'/SHG/{watershed["name"]}/{item["dss_cpart"]}/{item["dss_dpart"]}/{item["dss_epart"]}/{item["dss_fpart"]}/',
                data,
                grid_info
            )

    return os.path.abspath(outfile)