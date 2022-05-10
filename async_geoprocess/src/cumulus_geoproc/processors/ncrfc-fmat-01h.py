"""North Central River Forecast Center

Forecast Mesoscale Analysis Surface Temperature 01Hr
"""


import os
import re
from datetime import datetime, timezone

import pyplugs
from cumulus_geoproc import logger, utils
from cumulus_geoproc.utils import boto
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
        bucket, key = src.split("/", maxsplit=1)
        logger.debug(f"s3_download_file({bucket=}, {key=})")

        src_ = boto.s3_download_file(bucket=bucket, key=key, dst=dst)
        logger.debug(f"S3 Downloaded File: {src_}")

        for grib in gdal.ReadDir(f"/vsitar/{src_}"):
            try:
                filename_ = utils.file_extension(grib, suffix=".tif")
                ds = gdal.Open(f"/vsitar/{src_}/{grib}")
                raster = ds.GetRasterBand(1)

                # Compile regex to get times from timestamp
                time_pattern = re.compile(r"\d+")

                valid_time_match = time_pattern.match(
                    raster.GetMetadataItem("GRIB_VALID_TIME")
                )
                valid_time = (
                    datetime.fromtimestamp(
                        int(valid_time_match[0]), timezone.utc
                    ).isoformat()
                    if valid_time_match
                    else None
                )

                ref_time_match = time_pattern.match(
                    raster.GetMetadataItem("GRIB_REF_TIME")
                )
                ref_time = (
                    datetime.fromtimestamp(
                        int(ref_time_match[0]), timezone.utc
                    ).isoformat()
                    if ref_time_match
                    else None
                )

                gdal.Translate(
                    tif := os.path.join(dst, filename_),
                    ds,
                    format="COG",
                    bandList=[1],
                    creationOptions=[
                        "RESAMPLING=AVERAGE",
                        "OVERVIEWS=IGNORE_EXISTING",
                        "OVERVIEW_RESAMPLING=AVERAGE",
                        "NUM_THREADS=ALL_CPUS",
                    ],
                )

                # Append dictionary object to outfile list
                outfile_list.append(
                    {
                        "filetype": acquirable,
                        "file": tif,
                        "datetime": valid_time,
                        "version": ref_time,
                    }
                )
            except RuntimeError as ex:
                logger.error(f"{type(ex).__name__}: {this}: {ex}")
                continue

    except (RuntimeError, KeyError, Exception) as ex:
        logger.error(f"{type(ex).__name__}: {this}: {ex}")
    finally:
        ds = None
        raster = None

    return outfile_list


if __name__ == "__main__":
    pass
