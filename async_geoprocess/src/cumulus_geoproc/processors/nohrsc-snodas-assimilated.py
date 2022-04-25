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
        # extract the member from the tar using this pattern
        member_pattern = re.compile(r"ssm1054_\d+.\d+/ssm1054_\d+.nc.gz")
        with tarfile.open(src) as tar:
            for member in tar.getmembers():
                if member_pattern.match(member.name):
                    tar.extract(member, path=dst)

                    # decompress the extracted memeber
                    snodas_assim = utils.decompress(os.path.join(dst, member.name), dst)

                    ds = gdal.Open(snodas_assim, gdal.GA_ReadOnly)

                    valid_time = datetime.fromisoformat(
                        ds.GetMetadataItem("Data#stop_date")
                    )

                    gdal.Translate(
                        tif := utils.file_extension(snodas_assim),
                        ds,
                    )

                    # Append dictionary object to outfile list
                    outfile_list.append(
                        {
                            "filetype": acquirable,
                            "file": tif,
                            "datetime": valid_time,
                            "version": None,
                        }
                    )
                    break

    except (RuntimeError, KeyError, Exception) as ex:
        logger.error(f"{type(ex).__name__}: {this}: {ex}")
    finally:
        ds = None

    return outfile_list


if __name__ == "__main__":
    pass
