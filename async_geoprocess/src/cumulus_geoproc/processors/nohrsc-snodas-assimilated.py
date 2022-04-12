"""NOHRSC SNODAS Assimilated

Inside the original assim_layers_YYYYMMDDHH.tar file:
Inside a folder that looks like: ssm1054_2022012212.20220122134004 (without the word 'east')
There is a file that looks like: ssm1054_2022012212.nc.gz
Need to uncompress that NetCDF file
"""

# TODO: Refactor to new geoprocess package

import os
import re
import tarfile
from datetime import datetime

from cumulus_geoproc import utils
from cumulus_geoproc.utils import cgdal


from osgeo import gdal


def get_stop_date(gridfile):
    try:
        dataset = gdal.Open(f"NETCDF:{gridfile}:Data")
        meta = dataset.GetMetadata()
        return meta["Data#stop_date"]

    except Exception as e:
        # logger.error(e)
        return None

    finally:
        if dataset is not None:
            dataset = None


import pyplugs

this = os.path.basename(__file__)


# @pyplugs.register
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

    # logger.debug(infile)

    working_dir = os.path.dirname(src)
    r = re.compile("ssm1054_\d{10}.\d{14}/ssm1054_\d{10}.nc.gz")
    tar = tarfile.open(src)

    # Scan through the files in the tar file to find the compressed netcdf file.
    # Example Result: <TarInfo 'ssm1054_2022013112.20220131181006/ssm1054_2022013112.nc.gz' at 0x7f2dbc1a9e80>
    member_to_extract = [m for m in tar.getmembers() if r.match(m.name)][0]

    # This will extract the file, but leave it in it's original folder
    # You will reference the folder/filename to access the nc.gz file
    # extract_filename = os.path.basename(member_to_extract.name)
    tar.extract(member_to_extract, path=working_dir)

    # ex: /tmp/xyz/ssm1054_2022013112.20220131181006/ssm1054_2022013112.nc.gz
    compressed_file = os.path.join(working_dir, member_to_extract.name)

    # unzip the file and move it to the working_dir (instead of the member sub dir)
    uncompressed_file = utils.decompress(src, dst)

    tar.close()

    stop_date = get_stop_date(uncompressed_file)
    if stop_date is None:
        return outfile_list

    # Compile regex to get times from timestamp
    time_pattern = re.compile(r"\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}")
    valid_time_match = time_pattern.match(stop_date)
    valid_time = (
        datetime.strptime(stop_date + " +0000", "%Y-%m-%d %H:%M:%S %z").isoformat()
        if valid_time_match
        else None
    )

    if valid_time is None:
        return outfile_list

    translate_options = cgdal.gdal_translate_options(
        creationOptions=["TILED=YES", "COMPRESS=DEFLATE"]
    )

    ds = gdal.Open(uncompressed_file, gdal.GA_ReadOnly)
    gdal.Translate(
        tif := utils.file_extension(uncompressed_file),
        ds,
        **translate_options,
    )

    # Append dictionary object to outfile list
    outfile_list.append(
        {
            "filetype": "nohrsc-snodas-swe-corrections",
            "file": tif,
            "datetime": valid_time,
            "version": None,
        }
    )

    return outfile_list
