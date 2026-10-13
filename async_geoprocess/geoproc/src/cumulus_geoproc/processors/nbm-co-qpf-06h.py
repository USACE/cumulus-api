"""National Blend of Models (NBM)

CONUS 1hour Forecasted Airtemp and QPF
"""


import re
from datetime import datetime, timezone
from pathlib import Path

import pyplugs
from osgeo import gdal

from cumulus_geoproc import logger
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

    attr = {
        "GRIB_ELEMENT": "QPF06",
        "GRIB_SHORT_NAME": "0\\-SFC",
    }

    try:
        filename = Path(src).name

        # Take the source path as the destination unless defined.
        # User defined `dst` not programatically removed unless under
        # source's temporary directory.
        if dst is None:
            dst = Path(src).parent

        ds = gdal.Open(src)
        gdal_info = gdal.Info(ds, format="json")

        if (band_number := cgdal.band_from_json(gdal_info, attr, True)) is None:
            raise Exception("Band number not found for attributes: {attr}")

        logger.debug(f"Band number '{band_number}' found for attributes {attr}")

        raster = ds.GetRasterBand(band_number)

        # Get Datetime from String Like "1599008400 sec UTC"
        time_pattern = re.compile("\\d+")
        valid_time_match = time_pattern.match(raster.GetMetadataItem("GRIB_VALID_TIME"))
        dt_valid = datetime.fromtimestamp(int(valid_time_match[0]), timezone.utc)

        ref_time_match = time_pattern.match(raster.GetMetadataItem("GRIB_REF_TIME"))
        dt_ref = datetime.fromtimestamp(int(ref_time_match[0]), timezone.utc)

        filename_parts = filename.split(".")
        filename_parts.insert(1, dt_valid.strftime("%Y%m%d%H"))
        filename_dst = (
            Path(dst).joinpath(".".join(filename_parts)).with_suffix(".tif").as_posix()
        )

        cgdal.gdal_translate_w_options(
            tif := filename_dst,
            ds,
            bandList=[band_number],
        )

        # validate COG
        # if (validate := cgdal.validate_cog("-q", tif)) == 0:
        #     logger.debug(f"Validate COG = {validate}\t{tif} is a COG")

        outfile_list.append(
            {
                "filetype": acquirable,
                "file": tif,
                "datetime": dt_valid.isoformat(),
                "version": dt_ref.isoformat(),
            },
        )
        logger.debug(f"Appended Payload: {outfile_list[-1]}")

    except (RuntimeError, KeyError) as ex:
        logger.error(
            "{}: {}: {}".format(
                type(ex).__name__,
                Path(__file__).name,
                ex,
            )
        )
    finally:
        # closing the data source
        ds = None
        raster = None

    return outfile_list
