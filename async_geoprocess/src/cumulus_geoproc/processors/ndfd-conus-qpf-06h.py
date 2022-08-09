"""
# NDFD CONUS QPF 6 hour
"""


import os
import re
from datetime import datetime, timezone
from string import Template

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
        filename_ = utils.file_extension(filename, suffix="")

        filename_temp = Template("${filename}-${ymd}.tif")

        # Take the source path as the destination unless defined.
        # User defined `dst` not programatically removed unless under
        # source's temporary directory.
        if dst is None:
            dst = os.path.dirname(src)

        ds = gdal.Open(src)

        count = ds.RasterCount
        time_pattern = re.compile(r"\d+")
        for band_number in range(1, count + 1):
            try:
                raster = ds.GetRasterBand(band_number)

                valid_time_match = time_pattern.match(
                    raster.GetMetadataItem("GRIB_VALID_TIME")
                )
                vtime = datetime.fromtimestamp(int(valid_time_match[0]), timezone.utc)

                ref_time_match = time_pattern.match(
                    raster.GetMetadataItem("GRIB_REF_TIME")
                )
                rtime = datetime.fromtimestamp(int(ref_time_match[0]), timezone.utc)

                _filename = filename_temp.substitute(
                    filename=filename_, ymd=vtime.strftime("%Y%m%d%H%M")
                )
                logger.debug(f"New Filename: {_filename}")

                cgdal.gdal_translate_w_options(
                    tif := os.path.join(dst, _filename),
                    ds,
                )

                # validate COG
                if (validate := cgdal.validate_cog("-q", tif)) == 0:
                    logger.debug(f"Validate COG = {validate}\t{tif} is a COG")

                outfile_list.append(
                    {
                        "filetype": acquirable,
                        "file": tif,
                        "datetime": vtime.isoformat(),
                        "version": rtime.isoformat(),
                    }
                )
            except (RuntimeError, Exception) as ex:
                logger.error(f"{type(ex).__name__}: {this}: {ex}")
            finally:
                continue

    except (RuntimeError, KeyError) as ex:
        logger.error(f"{type(ex).__name__}: {this}: {ex}")
    finally:
        ds = None
        raster = None

    return outfile_list


if __name__ == "__main__":
    ...
