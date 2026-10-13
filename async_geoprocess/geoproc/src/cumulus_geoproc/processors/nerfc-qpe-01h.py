"""
# Northeast River Forecast Center (NERFC)

"""


import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import pyplugs
from osgeo import gdal

from cumulus_geoproc import logger, utils
from cumulus_geoproc.utils import cgdal

gdal.UseExceptions()


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
        # Source and Destination as Paths
        # take the source path as the destination unless defined.
        src_path = Path(src)
        if dst is None:
            dst_path = src_path.parent
        else:
            dst_path = Path(dst)

        try:
            ds = gdal.Open("/vsigzip/" + str(src_path))
        except RuntimeError as err:
            logger.warning(err)
            logger.warning(f'gunzip "{src}" and use as source file')
            src_unzip = utils.decompress(src, str(dst_path))
            ds = gdal.Open(src_unzip)

        raster = ds.GetRasterBand(1)

        # Get Datetime from String Like "1599008400 sec UTC"
        time_pattern = re.compile("\\d+")
        time_str = raster.GetMetadataItem("GRIB_VALID_TIME")
        valid_time_match = time_pattern.match(time_str)

        if valid_time_match:
            dt_valid = datetime.fromtimestamp(int(valid_time_match[0]), timezone.utc)
        else:
            raise Exception('No match to "GRIB_VALID_TIME"')

        cgdal.gdal_translate_w_options(
            tif := str(dst_path / f'qpe.{dt_valid.strftime("%Y%m%d_%H%M")}.tif'),
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

    except (RuntimeError, KeyError, Exception) as ex:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback_details = {
            "filename": os.path.basename(exc_traceback.tb_frame.f_code.co_filename),
            "line number": exc_traceback.tb_lineno,
            "method": exc_traceback.tb_frame.f_code.co_name,
            "type": exc_type.__name__,
            "message": exc_value,
        }
        for k, v in traceback_details.items():
            logger.error(f"{k}: {v}")

    finally:
        ds = None

    return outfile_list
