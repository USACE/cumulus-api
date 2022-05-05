"""NOHRSC SNODAS Assimilated

Inside the original assim_layers_YYYYMMDDHH.tar file:
Inside a folder that looks like: ssm1054_2022012212.20220122134004 (without the word 'east')
There is a file that looks like: ssm1054_2022012212.nc.gz
Need to uncompress that NetCDF file
"""


import os
import re
import tarfile
from datetime import datetime

import pyplugs
from cumulus_geoproc import logger, utils
from cumulus_geoproc.utils import boto, cgdal
from osgeo import gdal

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

        # extract the member from the tar using this pattern
        member_pattern = re.compile(r"ssm1054_\d+.\d+/ssm1054_\d+.nc.gz")
        with tarfile.open(src_) as tar:
            for member in tar.getmembers():
                if member_pattern.match(member.name):
                    tar.extract(member, path=dst)

                    filename = os.path.join(dst, member.name)

                    # decompress the extracted member
                    snodas_assim = utils.decompress(filename, dst)
                    logger.debug(f"{snodas_assim=}")

                    filename_ = utils.file_extension(snodas_assim)

                    ds = gdal.Open(snodas_assim)

                    # raster = ds.GetRasterBand(1)

                    # valid_time = datetime.fromisoformat(
                    #     raster.GetMetadataItem("stop_date")
                    # )
                    # no_data = raster.GetMetadataItem("_FillValue")

                    # gdal.Translate(
                    #     tif := os.path.join(dst, filename_),
                    #     ds,
                    #     format="COG",
                    #     bandList=[1],
                    #     noData=no_data,
                    #     creationOptions=[
                    #         "RESAMPLING=AVERAGE",
                    #         "OVERVIEWS=IGNORE_EXISTING",
                    #         "OVERVIEW_RESAMPLING=AVERAGE",
                    #         "NUM_THREADS=ALL_CPUS",
                    #     ],
                    # )

                    # # validate COG
                    # if (validate := cgdal.validate_cog("-q", tif)) == 0:
                    #     logger.info(f"Validate COG = {validate}\t{tif} is a COG")

                    # # Append dictionary object to outfile list
                    # outfile_list.append(
                    #     {
                    #         "filetype": acquirable,
                    #         "file": tif,
                    #         "datetime": valid_time,
                    #         "version": None,
                    #     }
                    # )
                    # break

    except (RuntimeError, KeyError, Exception) as ex:
        logger.error(f"{type(ex).__name__}: {this}: {ex}")
    finally:
        ds = None

    return outfile_list


if __name__ == "__main__":
    pass
