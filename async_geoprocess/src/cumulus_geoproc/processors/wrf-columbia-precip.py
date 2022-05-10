"""WRF Columbia Precipitation
"""

import os
import re
from datetime import datetime, timedelta, timezone

import pyplugs
from cumulus_geoproc import logger
from cumulus_geoproc.utils import boto, cgdal
from netCDF4 import Dataset
from osgeo import gdal, osr

gdal.UseExceptions()

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
    acquirable = "wrf-columbia-precip"
    """

    outfile_list = []

    ncds = None
    try:
        bucket, key = src.split("/", maxsplit=1)
        logger.debug(f"s3_download_file({bucket=}, {key=})")

        src_ = boto.s3_download_file(bucket=bucket, key=key, dst=dst)
        logger.debug(f"S3 Downloaded File: {src_}")

        ncds = Dataset(src_, "r")
        lon = ncds.variables["lon"][:]
        lat = ncds.variables["lat"][:]
        var = ncds.variables["var"][:]
        time_ = ncds.variables["time"]

        time_pattern = re.compile(r"\w+ \w+ (\d{4}-\d{2}-\d{2} \d+:\d+:\d+)")
        time_str = time_pattern.match(time_.units)
        since_time = datetime.fromisoformat(time_str[1]).replace(tzinfo=timezone.utc)

        nctimes = (since_time + timedelta(hours=int(td)) for td in time_)

        xmin, ymin, xmax, ymax = lon.min(), lat.min(), lon.max(), lat.max()
        for i, nctime in enumerate(nctimes):
            bandx = var[i]
            nctime_str = datetime.strftime(nctime, "%Y_%m_%d_T%H_%M")
            nrows, ncols = bandx.shape
            xres = (xmax - xmin) / float(ncols)
            yres = (ymax - ymin) / float(nrows)

            geotransform = (xmin, xres, 0, ymax, 0, -yres)

            raster = gdal.GetDriverByName("GTiff").Create(
                tmptif := os.path.join(
                    dst, src.replace(".nc", f"-{nctime_str}.tmp.tif")
                ),
                xsize=ncols,
                ysize=nrows,
                bands=1,
                eType=gdal.GDT_Float32,
            )
            raster.SetGeoTransform(geotransform)
            srs = osr.SpatialReference()
            srs.ImportFromEPSG(4326)

            raster.SetProjection(srs.ExportToWkt())
            band = raster.GetRasterBand(1)
            band.WriteArray(bandx)
            raster.FlushCache()
            raster = None

            cgdal.gdal_translate_w_overviews(
                tif := os.path.join(dst, src.replace(".nc", f"-{nctime_str}.tif")),
                tmptif,
                translate_options={
                    "format": "COG",
                    "bandList": [1],
                    "outputBounds": [-337997.806, 812645.371, 854002.194, -535354.629],
                    "outputSRS": "+proj=lcc +lat_1=45 +lat_2=45 +lon_0=-120 +lat_0=45.80369 +x_0=0 +y_0=0 +a=6370000 +b=6370000 +units=m",
                    "creationOptions": [
                        "RESAMPLING=AVERAGE",
                        "OVERVIEWS=IGNORE_EXISTING",
                        "OVERVIEW_RESAMPLING=AVERAGE",
                        "NUM_THREADS=ALL_CPUS",
                    ],
                },
            )

            # validate COG
            if (validate := cgdal.validate_cog("-q", tif)) == 0:
                logger.info(f"Validate COG = {validate}\t{tif} is a COG")

            try:
                os.remove(tmptif)
            except OSError as ex:
                print(ex)

            outfile_list.append(
                {
                    "filetype": acquirable,
                    "file": tif,
                    "datetime": nctime.isoformat(),
                    "version": datetime.utcnow(),
                }
            )

    except Exception as ex:
        print(ex)
    finally:
        if ncds:
            ncds.close()
        raster = None

    return outfile_list


if __name__ == "__main__":
    pass
