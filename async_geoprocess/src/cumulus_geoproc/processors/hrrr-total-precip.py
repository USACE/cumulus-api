"""
# High Resolution Rapid Refresh (HRRR) Total Precipitation

## HRRR file source:
    https://nomads.ncep.noaa.gov/pub/data/nccf/com/hrrr/prod/

## 2022-04-29 Update:
    HRRR index files (hrrr_filename.grib2.idx) are used to determine the
    ever changing '01 hr Total Precipitation' raster band number.  Archived
    HRRR products do not have idx files saved in S3, so this processor
    tries to account for that.
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
        attr = {
            "GRIB_ELEMENT": "APCP",
            "GRIB_COMMENT": "precipitation",
            "GRIB_UNIT": "[kg/(m^2)]",
        }

        filename = os.path.basename(src)
        filename_dst = utils.file_extension(filename)

        # Take the source path as the destination unless defined.
        # User defined `dst` not programatically removed unless under
        # source's temporary directory.
        if dst is None:
            dst = os.path.dirname(src)

        # open the hrrr.grib2 file
        ds = gdal.Open(src)

        # Can't use index file with product downloaded by handler
        # Successful download means we have the idx we need
        # idx_file = key + ".idx"

        # if hrrridx := boto.s3_download_file(bucket=bucket, key=idx_file, dst=dst):
        #     idx = hrrr.HrrrIdx()
        #     with open(hrrridx, "r") as fh:
        #         for line in fh.readlines():
        #             idx.linex(line)
        #             # This if statement means Total Precip for 01 hr forecast
        #             if idx.element == "APCP" and (
        #                 idx.forecast_hour == 0 or idx.forecast_hour == -1
        #             ):
        #                 band_number = idx.raster_band
        #     if band_number is None:
        #         raise Exception("Band number not found in idx: {hrrridx}")
        #     logger.debug(f"Band number '{band_number}' found in {hrrridx}")
        # else:
        #     if (band_number := cgdal.find_band(ds, attr)) is None:
        #         raise Exception(f"Band number not found for attributes: {attr}")
        #     print(f"Band number '{band_number}' found for attributes {attr}")

        if (band_number := cgdal.find_band(ds, attr)) is None:
            raise Exception(f"Band number not found for attributes: {attr}")

        logger.debug(f"Band number '{band_number}' found for attributes {attr}")

        raster = ds.GetRasterBand(band_number)

        # Get Datetime from String Like "1599008400 sec UTC"
        time_pattern = re.compile(r"\d+")
        valid_time_match = time_pattern.match(raster.GetMetadataItem("GRIB_VALID_TIME"))
        dt_valid = datetime.fromtimestamp(int(valid_time_match[0]), timezone.utc)
        ref_time_match = time_pattern.match(raster.GetMetadataItem("GRIB_REF_TIME"))
        dt_ref = datetime.fromtimestamp(int(ref_time_match[0]), timezone.utc)

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
                "version": dt_ref.isoformat(),
            },
        ]
    except (RuntimeError, KeyError, Exception) as ex:
        logger.error(f"{type(ex).__name__}: {this}: {ex}")
    finally:
        ds = None
        raster = None

    return outfile_list
