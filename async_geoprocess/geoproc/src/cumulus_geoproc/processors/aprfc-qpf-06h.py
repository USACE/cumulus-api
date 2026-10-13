"""
# Alaska Pacific River Forecast Center

## QPF 06 hour total precipitation
"""


import os
import sys
import pyplugs

from cumulus_geoproc import logger
from cumulus_geoproc.utils import cgdal


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
        attr = {"GRIB_ELEMENT": "APCP"}
        # determine the path and open the file in gdal
        ds, src_path, dst_path = cgdal.openfileGDAL(src, dst, GDALAccess="read_only")

        # Grad the grid from the band
        if (band_number := cgdal.find_band(ds, attr)) is None:
            raise Exception("Band number not found for attributes: {attr}")

        logger.debug(f"Band number '{band_number}' found for attributes {attr}")

        raster = ds.GetRasterBand(band_number)

        # Get Datetime from String Like "1599008400 sec UTC"
        dt_valid = cgdal.getDate(raster, src_path, "GRIB_VALID_TIME", None, None)
        dt_version = cgdal.getDate(raster, src_path, "GRIB_REF_TIME", None, None)

        cgdal.gdal_translate_w_options(
            tif := os.path.join(
                dst,
                f'{acquirable}.{dt_version.strftime("%Y%m%d_%H%M")}.{dt_valid.strftime("%Y%m%d_%H%M")}.tif',
            ),
            ds,
            bandList=[band_number],
        )

        # validate COG
        if (validate := cgdal.validate_cog("-q", tif)) == 0:
            logger.debug(f"Validate COG = {validate}\t{tif} is a COG")

        outfile_list = [
            {
                "filetype": acquirable,
                "file": tif,
                "datetime": dt_valid.isoformat(),
                "version": dt_version.isoformat(),
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
        raster = None

    return outfile_list
