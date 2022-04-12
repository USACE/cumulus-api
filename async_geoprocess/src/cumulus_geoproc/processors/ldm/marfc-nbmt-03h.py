"""Middle Atlantic River Forecast Center

National Blend of Models Surface Temperature 3 hour
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
    grib_element = "TMP"

    outfile_list = list()

    filename = os.path.basename(src)
    filename_ = utils.file_extension(filename)

    try:

        ds = gdal.Open("/vsis3_streaming/" + src)
        fileinfo = gdal.Info(ds, format="json")

        logger.debug(f"File Info: {fileinfo}")

        # figure out the band number
        band_number = None
        for band in fileinfo["bands"]:
            band_number = band["band"]
            band_meta = band["metadata"][""]
            valid_time = band_meta["GRIB_VALID_TIME"]
            reference_time = band_meta["GRIB_REF_TIME"]
            if (
                hasattr(band_meta, "GRIG_ELEMENT")
                and band_meta["GRIB_ELEMENT"].upper() == grib_element
            ):
                break

        # Get Datetime from String Like "1599008400 sec UTC"
        time_pattern = re.compile(r"\d+")
        valid_time_match = time_pattern.match(valid_time)
        reference_time_match = time_pattern.match(reference_time)
        dt_valid = datetime.fromtimestamp(int(valid_time_match[0]), timezone.utc)
        dt_reference = datetime.fromtimestamp(
            int(reference_time_match[0]), timezone.utc
        )

        # Extract Band; Convert to COG
        translate_options = cgdal.gdal_translate_options(bandList=[band_number])
        gdal.Translate(
            temp_file := os.path.join(dst, filename_),
            ds,
            **translate_options,
        )

        # closing the data source
        ds = None

        outfile_list = [
            {
                "filetype": acquirable,
                "file": temp_file,
                "datetime": dt_valid.isoformat(),
                "version": dt_reference.isoformat(),
            },
        ]
    except RuntimeError as ex:
        logger.error(f"{type(ex).__name__}: {this}: {ex}")
    except KeyError as ex:
        logger.error(f"{type(ex).__name__}: {this}: {ex}")

    return outfile_list
