"""NDFD CONUS QPF 6 hour
"""


import os
import re
from datetime import datetime, timezone
from string import Template

import pyplugs
from cumulus_geoproc import logger, utils
from cumulus_geoproc.utils import boto, cgdal
from osgeo import gdal

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
    """
    outfile_list = []

    try:
        filename = os.path.basename(src)
        filename_ = utils.file_extension(filename, suffix="")

        filename_temp = Template("${filename}-${ymd}.tif")

        bucket, key = src.split("/", maxsplit=1)
        logger.debug(f"s3_download_file({bucket=}, {key=})")

        src_ = boto.s3_download_file(bucket=bucket, key=key, dst=dst)
        logger.debug(f"S3 Downloaded File: {src_}")

        ds = gdal.Open(src_)

        count = ds.RasterCount
        time_pattern = re.compile(r"\d+")
        for band_number in range(1, count + 1):
            try:
                raster = ds.GetRasterBand(band_number)

                valid_time_match = time_pattern.match(
                    raster.GetMetadataItem("GRIB_VALID_TIME")
                )
                vtime = datetime.fromtimestamp(int(valid_time_match[0]), timezone.utc)

                ref_time_match = time_pattern.match(
                    raster.GetMetadataItem("GRIB_REF_TIME")
                )
                rtime = datetime.fromtimestamp(int(ref_time_match[0]), timezone.utc)

                _filename = filename_temp.substitute(
                    filename=filename_, ymd=vtime.strftime("%Y%m%d%H%M")
                )
                logger.debug(f"New Filename: {_filename}")

                gdal.Translate(
                    tif := os.path.join(dst, _filename),
                    ds,
                    format="COG",
                    bandList=[band_number],
                    creationOptions=[
                        "RESAMPLING=AVERAGE",
                        "OVERVIEWS=IGNORE_EXISTING",
                        "OVERVIEW_RESAMPLING=AVERAGE",
                        "NUM_THREADS=ALL_CPUS",
                    ],
                )

                # validate COG
                if (validate := cgdal.validate_cog("-q", tif)) == 0:
                    logger.debug(f"Validate COG = {validate}\t{tif} is a COG")

                outfile_list.append(
                    {
                        "filetype": acquirable,
                        "file": tif,
                        "datetime": vtime.isoformat(),
                        "version": rtime.isoformat(),
                    }
                )
            except (RuntimeError, Exception) as ex:
                logger.error(f"{type(ex).__name__}: {this}: {ex}")
            finally:
                continue

    except (RuntimeError, KeyError) as ex:
        logger.error(f"{type(ex).__name__}: {this}: {ex}")
    finally:
        ds = None
        raster = None

    return outfile_list


if __name__ == "__main__":
    pass
