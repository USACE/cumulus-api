"""Colorado Basin River Forecast Center (CBRFC)

Multisensor Precipitation Estimates (MPE)
"""


import os
import re
from datetime import datetime, timezone

import pyplugs
from cumulus_geoproc import logger, utils
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
    outfile_list = []

    try:
        attr = {"GRIB_ELEMENT": "APCP"}

        filename = os.path.basename(src)
        filename_ = utils.file_extension(filename)

        ds = gdal.Open("/vsis3_streaming/" + src)

        if (band_number := cgdal.find_band(ds, attr)) is None:
            raise Exception("Band number not found for attributes: {attr}")

        logger.debug(f"Band number '{band_number}' found for attributes {attr}")

        raster = ds.GetRasterBand(band_number)

        # Get Datetime from String Like "1599008400 sec UTC"
        time_pattern = re.compile(r"\d+")
        time_str = raster.GetMetadataItem("GRIB_VALID_TIME")
        valid_time_match = time_pattern.match(time_str)

        dt_valid = datetime.fromtimestamp(int(valid_time_match[0]), timezone.utc)

        # Extract Band; Convert to COG
        translate_options = cgdal.gdal_translate_options()
        gdal.Translate(
            temp_file := os.path.join(dst, filename_),
            raster.GetDataset(),
            **translate_options,
        )

        # closing the data source
        ds = None
        raster = None

        outfile_list = [
            {
                "filetype": acquirable,
                "file": temp_file,
                "datetime": dt_valid.isoformat(),
                "version": None,
            },
        ]
    except (RuntimeError, KeyError, Exception) as ex:
        logger.error(f"{type(ex).__name__}: {this}: {ex}")
    finally:
        ds = None
        raster = None

    return outfile_list
