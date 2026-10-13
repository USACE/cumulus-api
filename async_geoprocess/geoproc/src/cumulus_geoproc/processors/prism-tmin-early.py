"""
# PRISM Climate Group

Daily minimum temperature [averaged over all days in the month]

Reference: https://www.prism.oregonstate.edu/documents/PRISM_datasets.pdf
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
def process(*, src: str, dst: str = None, acquirable: str = None):
    """
    # Grid processor

    __Requires keyword only arguments (*)__

    Parameters
    ----------
    src : str
        path to input file for processing
    dst : str, optional
        path to temporary directory
    acquirable: str, optional
        acquirable slug

    Returns
    -------
    List[dict]
    ```
    {
        "filetype": str,         Matching database acquirable
        "file": str,             Converted file
        "datetime": str,         Valid Time, ISO format with timezone
        "version": str           Reference Time (forecast), ISO format with timezone
    }
    ```
    """

    outfile_list = []

    try:
        filename = os.path.basename(src)
        filename_dst = utils.file_extension(filename)

        # Take the source path as the destination unless defined.
        # User defined `dst` not programatically removed unless under
        # source's temporary directory.
        if dst is None:
            dst = os.path.dirname(str(src))

        file_ = utils.decompress(str(src), dst)
        logger.debug(f"Extract from zip: {file_}")

        # get date from filename like prism_tmin_us_25m_YYYYMMDD.zip
        date_str = filename.split('_')[-1].split('.')[0]
        format_str = "%Y%m%d"
        dt_valid = datetime.strptime(date_str, format_str).replace(
            hour=12, minute=0, second=0, tzinfo=timezone.utc
        )

        src_tif = os.path.join(file_, utils.file_extension(filename, suffix=".tif"))
        ds = gdal.Open(src_tif)

        cgdal.gdal_translate_w_options(
            tif := os.path.join(dst, filename_dst),
            ds,
        )

        # validate COG
        if (validate := cgdal.validate_cog("-q", tif)) == 0:
            logger.debug(f"Validate COG = {validate}\t{tif} is a COG")

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
