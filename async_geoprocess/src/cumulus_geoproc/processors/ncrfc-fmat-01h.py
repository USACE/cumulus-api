"""
# North Central River Forecast Center

Forecast Mesoscale Analysis Surface Temperature 01Hr
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
        if dst is None:
            dst = os.path.dirname(src)

        for grib in gdal.ReadDir(f"/vsitar/{src}"):
            try:
                filename = utils.file_extension(grib, suffix=".tif")

                ds = gdal.Open(f"/vsitar/{src}/{grib}")
                raster = ds.GetRasterBand(1)

                # Compile regex to get times from timestamp
                time_pattern = re.compile(r"\d+")

                valid_time_match = time_pattern.match(
                    raster.GetMetadataItem("GRIB_VALID_TIME")
                )
                valid_time = (
                    datetime.fromtimestamp(
                        int(valid_time_match[0]), timezone.utc
                    ).isoformat()
                    if valid_time_match
                    else None
                )

                ref_time_match = time_pattern.match(
                    raster.GetMetadataItem("GRIB_REF_TIME")
                )
                ref_time = (
                    datetime.fromtimestamp(
                        int(ref_time_match[0]), timezone.utc
                    ).isoformat()
                    if ref_time_match
                    else None
                )

                cgdal.gdal_translate_w_options(
                    tif := os.path.join(dst, filename),
                    ds,
                )

                # Append dictionary object to outfile list
                outfile_list.append(
                    {
                        "filetype": acquirable,
                        "file": tif,
                        "datetime": valid_time,
                        "version": ref_time,
                    }
                )
            except RuntimeError as ex:
                logger.error(f"{type(ex).__name__}: {this}: {ex}")
                continue

    except (RuntimeError, KeyError, Exception) as ex:
        logger.error(f"{type(ex).__name__}: {this}: {ex}")
    finally:
        ds = None
        raster = None

    return outfile_list


if __name__ == "__main__":
    ...
