"""Colorado Basin River Forecast Center (CBRFC)

Multisensor Precipitation Estimates (MPE)
"""


import os
import re
from datetime import datetime, timezone
from tempfile import TemporaryDirectory

import pyplugs
from cumulus_geoproc import logger, utils
from cumulus_geoproc.configurations import CUMULUS_PRODUCTS_BASEKEY
from cumulus_geoproc.utils import cgdal
from osgeo import gdal


@pyplugs.register
def process(src: str, dst: TemporaryDirectory, acquirable: str):
    """Grid processor

    Parameters
    ----------
    infile : str
        path to input file for processing
    outdir : str
        path to processor result

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

    filename = src.split("/")[-1]
    filename_ = utils.file_extension(filename)

    ds = gdal.Open(src)
    fileinfo = gdal.Info(ds, format="json")

    logger.debug(f"File Info: {fileinfo}")

    # for band in fileinfo["bands"]:
    #     band_number = str(band["band"])
    #     band_meta = band["metadata"][""]
    #     dtStr = band_meta["GRIB_VALID_TIME"]
    #     if "Total precipitation" in band_meta["GRIB_COMMENT"]:
    #         break

    # # Get Datetime from String Like "1599008400 sec UTC"
    # time_pattern = re.compile(r"\d+")
    # valid_time_match = time_pattern.match(dtStr)
    # dt = datetime.fromtimestamp(int(valid_time_match[0]), timezone.utc)

    # # print(f"Band number is {band_number}, date string is {dtStr}, and date is {dt}")

    # # # Extract Band 0 (QPE); Convert to COG
    # translate_options = cgdal.gdal_translate_options(bandList=[band_number])
    # gdal.Translate(
    #     temp_file := os.path.join(dst, filename_),
    #     src,
    #     **translate_options,
    # )

    # # closing the data source
    # ds = None

    # outfile_list = [
    #     {
    #         "filetype": acquirable,
    #         "file": temp_file,
    #         "datetime": dt.isoformat(),
    #         "version": None,
    #     },
    # ]

    return outfile_list
