import os
import numpy as np
import numpy.ma as ma
from osgeo import gdal
from affine import Affine
import config as CONFIG

from pydsstools.heclib.dss.HecDss import Open
from pydsstools.heclib.utils import gridInfo

def get_nodata_value(infile, band=1):
    """Get nodata value from input file. Default band=1"""

    ds = gdal.Open(infile)
    band = ds.GetRasterBand(band)
    nodatavalue = band.GetNoDataValue()
    ds = None
    band = None
    
    if nodatavalue is None:
        return 9999

    return nodatavalue


def write_contents_to_dssfile(outfile, watershed, items, callback, cellsize=2000, dst_srs="EPSG:5070"):

    HEC_WKT = '"PROJCS[\"USA_Contiguous_Albers_Equal_Area_Conic_USGS_version\",GEOGCS[\"GCS_North_American_1983\",DATUM[\"D_North_American_1983\",SPHEROID[\"GRS_1980\",6378137.0,298.257222101]],PRIMEM[\"Greenwich\",0.0],UNIT[\"Degree\",0.0174532925199433]],PROJECTION[\"Albers\"],PARAMETER[\"False_Easting\",0.0],PARAMETER[\"False_Northing\",0.0],PARAMETER[\"Central_Meridian\",-96.0],PARAMETER[\"Standard_Parallel_1\",29.5],PARAMETER[\"Standard_Parallel_2\",45.5],PARAMETER[\"Latitude_Of_Origin\",23.0],UNIT[\"Meter\",1.0]]"'

    with Open(outfile) as fid:

        item_length = len(items)
        for idx, item in enumerate(items):
            try:
                # Update progress at predefined interval
                if idx % CONFIG.PACKAGER_UPDATE_INTERVAL == 0 or idx == item_length-1:
                    callback(idx)
                
                infile = f'/vsis3_streaming/{item["bucket"]}/{item["key"]}'
                
                ds = gdal.Warp(
                    '/vsimem/projected.tif',
                    infile,
                    dstSRS=dst_srs,
                    outputType=gdal.GDT_Float64,
                    outputBounds=watershed['bbox'],
                    resampleAlg="bilinear",
                    targetAlignedPixels=True,
                    xRes=cellsize,
                    yRes=cellsize,
                )

                # Get the grid nodata
                nodatavalue = get_nodata_value(infile)
                # Get grid array
                data = ds.GetRasterBand(1).ReadAsArray().astype(np.dtype('float32'))
                # replace gridarray nodata values with dss accepted nodata value
                data = np.where((data == nodatavalue), np.nan, data)

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
                    ('data_type', item['dss_datatype'].lower()),
                    ('data_units', item['dss_unit'].lower()),
                    ('opt_crs_name', 'AlbersInfo'),
                    ('opt_lower_left_x', watershed['bbox'][0] / cellsize),
                    ('opt_lower_left_y', watershed['bbox'][1] / cellsize),
                ])
                    # ('opt_is_interval', True),
                    # ('opt_time_stamped', True),
                fid.put_grid(
                    f'/SHG/{watershed["name"]}/{item["dss_cpart"]}/{item["dss_dpart"]}/{item["dss_epart"]}/{item["dss_fpart"]}/',
                    data,
                    grid_info
                )
            except:
                print(f'Unable to process: {item["bucket"]}/{item["key"]}')
            finally:
                ds = None
                data = None

    return os.path.abspath(outfile)
