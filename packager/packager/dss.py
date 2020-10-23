import os
import numpy as np
import numpy.ma as ma
from osgeo import gdal
from affine import Affine

from pydsstools.heclib.dss.HecDss import Open
from pydsstools.heclib.utils import gridInfo


def write_contents_to_dssfile(outfile, basin, items, callback):

    cellsize = 2000

    with Open(outfile) as fid:

        for idx, item in enumerate(items):
            # Update progress
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
            xmin,ymax = geo_transform[0], geo_transform[3]
            affine_transform = Affine(cellsize,0,xmin,0,-cellsize,ymax)

            # Create HEC GridInfo Object
            grid_info = gridInfo()
            grid_info.update([
                ('grid_type','specified'),
                ('grid_crs', proj),
                ('grid_transform', affine_transform),
                ('data_type', item['dss_datatype'].lower()),
                ('data_units', item['dss_unit'].lower()),
                ('opt_time_stamped',False)
            ])

            fid.put_grid(
                f'/SHG/{basin["name"]}/DATA/{item["dss_dpart"]}/{item["dss_epart"]}/{item["dss_fpart"]}/',
                data,
                grid_info
            )
        
    return os.path.abspath(outfile)
