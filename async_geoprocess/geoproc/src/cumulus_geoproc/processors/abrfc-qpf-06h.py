"""
# Arkansas-Red Basin River Forecast Center

## QPF 06 hour total precipitation
"""


import os
import sys
import pyplugs

from cumulus_geoproc import logger
from cumulus_geoproc.utils import cgdal

SUBSET_NAME = "QPF_SFC"
SUBSET_DATATYPE = "32-bit floating-point"


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

    try:
        # determine the path and open the file in gdal
        ds, src_path, dst_path = cgdal.openfileGDAL(src, dst)

        ds = cgdal.findsubset(ds, [SUBSET_NAME, SUBSET_DATATYPE])

        version_datetime = cgdal.getDate(
            ds, src_path, "NC_GLOBAL#creationTime", "%Y%m%d%H", "\\d{10}", False
        )

        ds, lonLL, latLL, lonUR, latUR = cgdal.geoTransform_ds(ds, SUBSET_NAME)
        outfile_list = cgdal.subsetOutFile(
            ds,
            SUBSET_NAME,
            dst_path,
            acquirable,
            version_datetime,
            outputBounds=[lonLL, latUR, lonUR, latLL],
            outputSRS="EPSG:4326",
        )

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
