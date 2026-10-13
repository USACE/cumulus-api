"""
# Arkansas-Red Basin River Forecast Center

"""

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pyplugs
from cumulus_geoproc import logger
from cumulus_geoproc.utils import cgdal
from osgeo import gdal


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

    if dst is None:
        dst = Path(src).parent

    try:
        data_set = gdal.Open(src)

        outfile_list.append(
            {
                "filetype": acquirable,
                "file": "",
                "datetime": "",
                "version": None,
            }
        )

    except RuntimeError:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback_details = {
            "filename": Path(exc_traceback.tb_frame.f_code.co_filename).name,
            "line number": exc_traceback.tb_lineno,
            "method": exc_traceback.tb_frame.f_code.co_name,
            "type": exc_type.__name__,
            "message": exc_value,
        }
        for k, v in traceback_details.items():
            logger.error("{%s}: {%s}".format(k, v))
        return outfile_list
    finally:
        data_set = None

    return outfile_list
