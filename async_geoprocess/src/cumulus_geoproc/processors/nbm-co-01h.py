"""National Blend of Models (NBM)

CONUS 1hour Forecasted Airtemp and QPF
"""


import os
import re
from datetime import datetime, timezone
from uuid import uuid4

import pyplugs
from cumulus_geoproc import logger, utils
from cumulus_geoproc.configurations import CUMULUS_PRODUCTS_BASEKEY
from cumulus_geoproc.utils import cgdal
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

    filename = os.path.basename(src)
    filename_ = utils.file_extension(filename)

    filetype_elements = {
        "nbm-co-airtemp": {"GRIB_ELEMENT": "T", "GRIB_SHORT_NAME": "0-SFC"},
        "nbm-co-qpf": {"GRIB_ELEMENT": "QPF01", "GRIB_SHORT_NAME": "0-SFC"},
    }

    try:
        ds = gdal.Open("/vsis3_streaming/" + src)
        fileinfo = gdal.Info(ds, format="json")

        # logger.debug(f"File Info: {fileinfo}")

        for filetype, grib_elements in filetype_elements.items():
            grib_element = grib_elements["GRIB_ELEMENT"]
            grib_short_name = grib_elements["GRIB_SHORT_NAME"]

            logger.debug(f"{filetype=}\t{grib_element=}\t{grib_short_name=}")

            try:
                # figure out the band number
                band_number = None
                for band in fileinfo["bands"]:
                    band_number = band["band"]
                    band_meta = band["metadata"][""]
                    valid_time = band_meta["GRIB_VALID_TIME"]
                    if (
                        band_meta["GRIB_ELEMENT"].upper() == grib_element
                        and band_meta["GRIB_SHORT_NAME"].upper() == grib_short_name
                    ):
                        break

                logger.debug(f"Band Number: {band_number}")

                # Get Datetime from String Like "1599008400 sec UTC"
                time_pattern = re.compile(r"\d+")
                valid_time_match = time_pattern.match(valid_time)
                dt_valid = datetime.fromtimestamp(
                    int(valid_time_match[0]), timezone.utc
                )

                # Extract Band; Convert to COG
                translate_options = cgdal.gdal_translate_options(bandList=[band_number])
                gdal.Translate(
                    temp_file := os.path.join(dst, filename_),
                    ds,
                    **translate_options,
                )

                outfile_list.append(
                    {
                        "filetype": filetype,
                        "file": temp_file,
                        "datetime": dt_valid.isoformat(),
                        "version": None,
                    },
                )
                logger.debug(f"Appended Payload: {outfile_list[-1]}")

            except RuntimeError as ex:
                logger.error(f"{type(ex).__name__}: {this}: {ex}")
                continue

    except RuntimeError as ex:
        logger.error(f"{type(ex).__name__}: {this}: {ex}")
    except KeyError as ex:
        logger.error(f"{type(ex).__name__}: {this}: {ex}")

    # closing the data source
    ds = None

    return outfile_list
