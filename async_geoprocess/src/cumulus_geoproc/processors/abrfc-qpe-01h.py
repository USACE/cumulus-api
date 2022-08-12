"""
# Arkansas-Red Basin River Forecast Center

## File Type

File type is netCDF-3 (version 3).  GDAL does `NOT` show any bands available
when viewing metadata (gdalinfo -json *netCDF_file*); therefore Python package
`netCDF4` is used to process these products.

"""


import os
from string import Template
from datetime import datetime, timedelta, timezone
import time
import numpy

import pyplugs
from cumulus_geoproc import logger
from cumulus_geoproc.utils import cgdal
from osgeo import gdal
from netCDF4 import Dataset

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

    proj4_template = Template(
        "+proj=stere +lat_ts=${lat_ts}"
        " +k_0=${k_0}"
        " +long_0=${long_0}"
        " +R=${radius}"
        " +x_0=0.0"
        " +y_0=0.0"
        " +units=m"
    )

    filename = os.path.basename(src)

    # Take the source path as the destination unless defined.
    # User defined `dst` not programatically removed unless under
    # source's temporary directory.
    if dst is None:
        dst = os.path.dirname(src)

    try:
        with Dataset(src, "r") as ncds:
            # Determine time dependencies

            nctime = ncds.variables["time"][:]
            dt_int32 = int(nctime.data[0])
            dt_valid = (UNIX_EPOCH + timedelta(hours=dt_int32)).replace(
                tzinfo=timezone.utc
            )

            lat = ncds.variables["y"][:]
            lon = ncds.variables["x"][:]
            xmin, ymin, xmax, ymax = lon.min(), lat.min(), lon.max(), lat.max()

            ncvar = ncds.variables["Total_precipitation"]
            nodata = ncvar.missing_value

            _, nrows, ncols = ncvar.shape

            xres = (xmax - xmin) / float(ncols)
            yres = (ymax - ymin) / float(nrows)

            geotransform = (xmin, xres, 0, ymax, 0, -yres)

            # Create a raster, set attributes, and define the spatial reference
            projection = ncds.variables["Polar_Stereographic"]

            proj4 = proj4_template.substitute(
                lat_ts=projection.latitude_of_projection_origin,
                k_0=projection.scale_factor_at_projection_origin,
                long_0=projection.longitude_of_projection_origin,
                radius=projection.earth_radius,
            )

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
            data = numpy.flipud(data_squeeze)

            band = raster.GetRasterBand(1)
            band.WriteArray(data)

            raster.FlushCache()
            raster = None

            cgdal.gdal_translate_w_options(
                tif := os.path.join(dst, f"{filename}.tif"),
                tmptif,
                outputBounds=[ncds.lon00, ncds.latNxNy, ncds.lonNxNy, ncds.lat00],
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
        logger.error(f"{type(ex).__name__}: {this}: {ex}")
    finally:
        raster = None

    return outfile_list
