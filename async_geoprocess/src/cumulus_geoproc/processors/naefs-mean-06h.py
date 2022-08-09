"""NAEFS Mean 6 hour
"""


import os
import re
from datetime import datetime, timezone
import numpy

import pyplugs
from cumulus_geoproc import logger
from cumulus_geoproc.utils import cgdal
from osgeo import gdal, osr
from netCDF4 import Dataset, num2date, date2index

this = os.path.basename(__file__)


@pyplugs.register
def process(src: str, dst: str, acquirable: str = None):
    """Grid processor

    Parameters
    ----------
    src : str
        path to input file for processing
    dst : str
        path to temporary directory created from worker thread
    acquirable: str
        acquirable slug

    Returns
    -------
    List[dict]
        {
            "filetype": str,         Matching database acquirable
            "file": str,             Converted file
            "datetime": str,         Valid Time, ISO format with timezone
            "version": str           Reference Time (forecast), ISO format with timezone
        }
    """
    outfile_list = []

    try:
        filename = os.path.basename(src)
        
        # Take the source path as the destination unless defined.
        # User defined `dst` not programatically removed unless under
        # source's temporary directory.
        if dst is None:
            dst = os.path.dirname(src)

        products = {"QPF": "naefs-mean-qpf-06h", "QTF": "naefs-mean-qtf-06h"}

        with Dataset(src, "r") as ncds:
            time_str = re.match(r"\d{4}-\d{2}-\d{2} \d+:\d+:\d+", ncds.date_created)
            date_created = datetime.fromisoformat(time_str[0]).replace(
                tzinfo=timezone.utc
            )

            lat = ncds.variables["y"][:]
            lon = ncds.variables["x"][:]
            xmin, ymin, xmax, ymax = lon.min(), lat.min(), lon.max(), lat.max()

            wkt = ncds.variables["crs"].crs_wkt
            logger.debug(f"WKT: {wkt}")

            nctime = ncds.variables["time"]
            for k, acquirable_ in products.items():
                logger.debug(f"Product Variable: {k}")
                logger.debug(f"Product Acquirable: {acquirable_}")
                ncvar = ncds.variables[k]
                nodata = ncvar._FillValue

                _, nrows, ncols = ncvar.shape

                xres = (xmax - xmin) / float(ncols)
                yres = (ymax - ymin) / float(nrows)
                geotransform = (xmin, xres, 0, ymax, 0, -yres)

                _data = None
                for dt in num2date(
                    nctime[:], nctime.units, only_use_cftime_datetimes=False
                ):
                    dt_valid = dt.replace(tzinfo=timezone.utc)
                    idx = date2index(dt, nctime)
                    nctime_str = datetime.strftime(dt, "%Y%m%d%H%M")

                    raster = gdal.GetDriverByName("GTiff").Create(
                        tmptif := os.path.join(
                            dst, filename.replace(".nc", f"-{k}-{nctime_str}-tmp.tif")
                        ),
                        xsize=ncols,
                        ysize=nrows,
                        bands=1,
                        eType=gdal.GDT_Float32,
                    )
                    raster.SetGeoTransform(geotransform)
                    srs = osr.SpatialReference()
                    srs.ImportFromWkt(wkt)

                    raster.SetProjection(wkt)
                    band = raster.GetRasterBand(1)

                    # Reference the following for reason to flip
                    # https://www.unidata.ucar.edu/support/help/MailArchives/netcdf/msg03585.html
                    # Basically, get the array sequence like other Tiffs
                    _data = ncvar[idx]
                    _data = numpy.flipud(_data)
                    band.WriteArray(_data)
                    raster.FlushCache()
                    raster = None

                    gdal.Translate(
                        tif := os.path.join(dst, tmptif.replace("-tmp.tif", ".tif")),
                        tmptif,
                        format="COG",
                        bandList=[1],
                        noData=nodata,
                        creationOptions=[
                            "RESAMPLING=BILINEAR",
                            "OVERVIEWS=IGNORE_EXISTING",
                            "OVERVIEW_RESAMPLING=BILINEAR",
                        ],
                    )

                    # validate COG
                    if (validate := cgdal.validate_cog("-q", tif)) == 0:
                        logger.debug(f"Validate COG = {validate}\t{tif} is a COG")

                    outfile_list.append(
                        {
                            "filetype": acquirable_,
                            "file": tif,
                            "datetime": dt_valid.isoformat(),
                            "version": date_created.isoformat(),
                        }
                    )
    except (RuntimeError, KeyError, Exception) as ex:
        logger.error(f"{type(ex).__name__}: {this}: {ex}")
    finally:
        raster = None

    return outfile_list


if __name__ == "__main__":
    ...
