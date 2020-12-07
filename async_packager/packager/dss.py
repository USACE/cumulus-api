import os
import numpy as np
import numpy.ma as ma
from osgeo import gdal
from affine import Affine

import config as CONFIG

from pydsstools.heclib.dss.HecDss import Open
from pydsstools.heclib.utils import gridInfo


def write_contents_to_dssfile(outfile, basin, items, callback):

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
                outputBounds=[basin['x_min'], basin['y_min'], basin['x_max'], basin['y_max']],
                resampleAlg="bilinear",
                targetAlignedPixels=True,
                xRes=cellsize,
                yRes=cellsize
            )

            # Raw Cell Values as Array
            data = ds.GetRasterBand(1).ReadAsArray().astype(np.dtype('float32'))

            # Projection
            proj = ds.GetProjection()
            # Affine Transform
            geo_transform = ds.GetGeoTransform()
            affine_transform = Affine.from_gdal(*geo_transform)

            # Create HEC GridInfo Object
            grid_info = gridInfo()
            grid_info.update([
                ('grid_type','specified-time'),
                ('grid_crs', proj),
                ('grid_transform', affine_transform),
                ('data_type', item['dss_datatype'].lower()),
                ('data_units', item['dss_unit'].lower()),
                ('opt_lower_left_x', basin['x_min'] / cellsize),
                ('opt_lower_left_y', basin['y_min'] / cellsize),
                ('opt_time_stamped',False)
            ])

            fid.put_grid(
                f'/SHG/{basin["name"]}/{item["dss_cpart"]}/{item["dss_dpart"]}/{item["dss_epart"]}/{item["dss_fpart"]}/',
                data,
                grid_info
            )
        
    return os.path.abspath(outfile)