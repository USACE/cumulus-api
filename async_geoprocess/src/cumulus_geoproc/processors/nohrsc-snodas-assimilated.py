from datetime import datetime, timedelta
import os
import re
import tarfile
import numpy as np
from datetime import datetime, timezone
from collections import namedtuple
from osgeo import gdal
from uuid import uuid4
from ..geoprocess.core.base import (
    info,
    translate,
    create_overviews,
    translate_cog,
    write_array_to_raster,
)
from ..handyutils.core import (
    change_file_extension,
    change_final_file_extension,
    gunzip_file,
)


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


@pyplugs.register
def process(infile, outdir):
    """Takes an infile to process and path to a directory where output files should be saved
    Returns array of objects [{ "filetype": "nohrsc_snodas_swe", "file": "file.tif", ... }, {}, ]
    """

    outfile_list = []

    # logger.debug(infile)

    """
    Inside the original assim_layers_YYYYMMDDHH.tar file:
    Inside a folder that looks like: ssm1054_2022012212.20220122134004 (without the word 'east')
    There is a file that looks like: ssm1054_2022012212.nc.gz
    Need to uncompress that NetCDF file
    """

    working_dir = os.path.dirname(infile)
    r = re.compile("ssm1054_\d{10}.\d{14}/ssm1054_\d{10}.nc.gz")
    tar = tarfile.open(infile)

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
    uncompressed_filename = change_file_extension(compressed_file, "nc")
    uncompressed_file = os.path.join(working_dir, uncompressed_filename)
    gunzip_file(compressed_file, uncompressed_file)

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

    cog = translate_cog(
        uncompressed_file,
        os.path.join(outdir, change_final_file_extension(uncompressed_file, "tif")),
    )

    # Append dictionary object to outfile list
    outfile_list.append(
        {
            "filetype": "nohrsc-snodas-swe-corrections",
            "file": cog,
            "datetime": valid_time,
            "version": None,
        }
    )

    return outfile_list
