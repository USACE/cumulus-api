"""
# NSIDC SWE v1
"""


import os
import re
from datetime import datetime, timedelta, timezone

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

    # Variables and their product slug
    nc_variables = {
        "SWE": "nsidc-ua-swe-v1",
        "DEPTH": "nsidc-ua-snowdepth-v1",
    }

    try:
        filename = os.path.basename(src)
        filename_dst = utils.file_extension(filename)

        # Take the source path as the destination unless defined.
        # User defined `dst` not programatically removed unless under
        # source's temporary directory.
        if dst is None:
            dst = os.path.dirname(src)

        for nc_variable, nc_slug in nc_variables.items():
            ds = gdal.Open(f"NETCDF:{src}:{nc_variable}")

            # set the start time
            time_pattern = re.compile(r"\w+ \w+ (\d{4}-\d{2}-\d{2})")
            day_since_str = time_pattern.match(ds.GetMetadataItem("time#units"))
            day_since = datetime.fromisoformat(day_since_str[1]).replace(
                tzinfo=timezone.utc
            )

            for band_number in range(1, ds.RasterCount + 1):
                # set the bands date
                raster = ds.GetRasterBand(band_number)
                delta_days = raster.GetMetadataItem("NETCDF_DIM_time")
                band_date = day_since + timedelta(days=int(delta_days))

                datetime_str = band_date.strftime("%Y%m%d")
                filename_ = utils.file_extension(
                    filename, suffix=f"_{datetime_str}_{nc_variable}.tif"
                )

                cgdal.gdal_translate_w_options(
                    tif := os.path.join(dst, filename_),
                    ds,
                )

                # validate COG
                if (validate := cgdal.validate_cog("-q", tif)) == 0:
                    logger.debug(f"Validate COG = {validate}\t{tif} is a COG")

                outfile_list.append(
                    {
                        "filetype": nc_slug,
                        "file": tif,
                        "datetime": band_date.isoformat(),
                        "version": None,
                    }
                )

    except RuntimeError as ex:
        logger.error(f"{type(ex).__name__}: {this}: {ex}")
    finally:
        ds = None

    return outfile_list


if __name__ == "__main__":
    ...
