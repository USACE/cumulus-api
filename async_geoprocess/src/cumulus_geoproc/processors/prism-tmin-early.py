"""PRISM Climate Group

Daily minimum temperature [averaged over all days in the month]

Reference: https://www.prism.oregonstate.edu/documents/PRISM_datasets.pdf
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

    outfile_list = list()

    try:
        filename = os.path.basename(src)
        filename_ = utils.file_extension(filename, suffix=".tif")

        bucket, key = src.split("/", maxsplit=1)
        logger.debug(f"s3_download_file({bucket=}, {key=})")

        # download the file to the current filesystem and extract
        src_ = boto.s3_download_file(bucket=bucket, key=key, dst=dst)
        logger.debug(f"S3 Downloaded File: {src_}")

        file_ = utils.decompress(src_, dst)
        logger.debug(f"Extract from zip: {file_}")

        # get date from filename like PRISM_ppt_early_4kmD2_yyyyMMdd_bil.zip
        time_pattern = re.compile(r"\w+_(?P<ymd>\d+)_\w+")
        m = time_pattern.match(filename)
        dt_valid = datetime.strptime(m.group("ymd"), "%Y%m%d").replace(
            hour=12, minute=0, second=0, tzinfo=timezone.utc
        )

        # Extract Band; Convert to COG
        src_bil = utils.file_extension(file_, suffix=".bil")
        ds = gdal.Open(src_bil)
        gdal.Translate(
            tif := os.path.join(dst, filename_),
            ds,
        )

        # closing the data source
        ds = None

        outfile_list = [
            {
                "filetype": acquirable,
                "file": tif,
                "datetime": dt_valid.isoformat(),
                "version": None,
            },
        ]
    except (RuntimeError, KeyError, IndexError) as ex:
        logger.error(f"{type(ex).__name__}: {this}: {ex}")
    finally:
        ds = None

    return outfile_list


if __name__ == "__main__":
    pass
