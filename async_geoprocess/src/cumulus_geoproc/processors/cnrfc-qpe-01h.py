"""
# California-Nevada Basin River Forecast Center

## File Type

File type is netCDF-3 (version 3); therefore, Python package
`netCDF4` is used to process these products.

"""


import os
import sys
import time
from datetime import datetime, timedelta, timezone
from tempfile import TemporaryDirectory

import numpy
import pyplugs
from cumulus_geoproc import logger, utils
from cumulus_geoproc.utils import cgdal
from netCDF4 import Dataset
from osgeo import gdal

this = os.path.basename(__file__)

UNIX_EPOCH = datetime(
    time.gmtime(0).tm_year,
    time.gmtime(0).tm_mon,
    time.gmtime(0).tm_mday,
    time.gmtime(0).tm_hour,
    time.gmtime(0).tm_min,
    time.gmtime(0).tm_sec,
)
"""datetime: uniform date for the start of time"""

xster = lambda hrap: hrap * 4762.5 - 401 * 4762.5
yster = lambda hrap: hrap * 4762.5 - 1601 * 4762.5


@pyplugs.register
def process(*, src: str, dst: str = None, acquirable: str = None):
    """
    # Grid processor

    __Requires keyword only arguments (*)__

    Parameters
    ----------
    src : str
        path to input file for processing
    dst : str, optional
        path to temporary directory
    acquirable: str, optional
        acquirable slug

    Returns
    -------
    List[dict]
    ```
    {
        "filetype": str,         Matching database acquirable
        "file": str,             Converted file
        "datetime": str,         Valid Time, ISO format with timezone
        "version": str           Reference Time (forecast), ISO format with timezone
    }
    ```
    """
    outfile_list = []

    proj4 = "+proj=stere +lat_ts=60 +k_0=1 +long_0=-105 +R=6371200 +x_0=0.0 +y_0=0.0 +units=m"

    filename = os.path.basename(src)

    # Take the source path as the destination unless defined.
    # User defined `dst` not programatically removed unless under
    # source's temporary directory.
    if dst is None:
        dst = os.path.dirname(src)

    try:
        # Using temporary directory for gzip because netCDF4 does not have a VSI like gdal
        tmpdir = TemporaryDirectory(dir=dst)
        src_ = utils.decompress(src, tmpdir.name)
        with Dataset(src_, "r") as ncds:
            ncvar = ncds.variables["qpe_grid"]

            # Determine time dependencies
            nctime = ncvar.validTimes
            dt_int32 = int(nctime[-1])
            dt_valid = (UNIX_EPOCH + timedelta(seconds=dt_int32)).replace(
                tzinfo=timezone.utc
            )

            nodata = ncvar.fillValue

            lonLL, latLL = ncvar.latLonLL
            lonUR, latUR = ncvar.latLonUR

            xmin, ymin = ncvar.gridPointLL
            xmax, ymax = ncvar.gridPointUR

            xmin = xster(xmin)
            xmax = xster(xmax)
            ymin = yster(ymin)
            ymax = yster(ymax)

            _, nrows, ncols = ncvar.shape

            xres = (xmax - xmin) / float(ncols)
            yres = (ymax - ymin) / float(nrows)

            geotransform = (xmin, xres, 0, ymax, 0, -yres)

            # Create a raster, set attributes, and define the spatial reference
            raster = gdal.GetDriverByName("GTiff").Create(
                tmptif := "/vsimem/{filename}-tmp.tif",
                xsize=ncols,
                ysize=nrows,
                eType=gdal.GDT_Float32,
            )

            raster.SetGeoTransform(geotransform)
            raster.SetProjection(proj4)

            # Reference the following for reason to flip
            # https://www.unidata.ucar.edu/support/help/MailArchives/netcdf/msg03585.html
            # Basically, get the array sequence like other Tiffs
            data_masked = ncvar[:]
            data_ndarray = data_masked.data
            data_squeeze = numpy.squeeze(data_ndarray)
            data = numpy.flipud(data_squeeze) * 25.4

            band = raster.GetRasterBand(1)
            band.WriteArray(data)

            raster.FlushCache()
            raster = None

            cgdal.gdal_translate_w_options(
                tif := os.path.join(dst, f"{filename}.tif"),
                tmptif,
                outputBounds=[lonLL, latUR, lonUR, latLL],
                outputSRS="EPSG:4326",
                noData=nodata,
            )

            # validate COG
            if (validate := cgdal.validate_cog("-q", tif)) == 0:
                logger.debug(f"Validate COG = {validate}\t{tif} is a COG")

            outfile_list.append(
                {
                    "filetype": acquirable,
                    "file": tif,
                    "datetime": dt_valid.isoformat(),
                    "version": None,
                }
            )
    except (RuntimeError, KeyError, Exception) as ex:
        # TODO: Implement this to all processors with method in __init__
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback_details = {
            "filename": os.path.basename(exc_traceback.tb_frame.f_code.co_filename),
            "line number": exc_traceback.tb_lineno,
            "method": exc_traceback.tb_frame.f_code.co_name,
            "type": exc_type.__name__,
            "message": exc_value,
        }
        for k, v in traceback_details.items():
            logger.error(f"{k}: {v}")
    finally:
        raster = None

    return outfile_list
