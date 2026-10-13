"""
# Northwest River Forecast Center (NWRFC)

## QTF 06 hour air temperature
"""


import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pyplugs
from osgeo import gdal

from cumulus_geoproc import logger, utils
from cumulus_geoproc.utils import cgdal

gdal.UseExceptions()

SUBSET_NAME = "QTF"
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
            ds = gdal.Open("/vsigzip/" + src)
        except RuntimeError as err:
            logger.warning(err)
            logger.warning(f'gunzip "{src}" and use as source file')
            src_unzip = utils.decompress(src, str(dst_path))
            ds = gdal.Open(src_unzip)

        subdatasets = ds.GetSubDatasets()

        for subdataset in subdatasets:
            subsetpath, datatype = subdataset
            if SUBSET_NAME in datatype and SUBSET_DATATYPE in datatype:
                ds = gdal.Open(subsetpath)
                break
            else:
                ds = None

        if ds is None:
            raise Exception(
                f"Did not find the sub-dataset we are lookingfor, {SUBSET_NAME} ({SUBSET_DATATYPE})"
            )

        # find the minutes since
        time_units = ds.GetMetadataItem("time#units")
        time_units_match = re.search(
            "\\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2}:\\d{2}", time_units
        )
        if time_units_match:
            since_time = datetime.fromisoformat(time_units_match[0]).replace(
                tzinfo=timezone.utc
            )
        else:
            since_time = datetime(1970, 1, 1, 0, 0).replace(tzinfo=timezone.utc)
            logger.info(f"Assuming since time {since_time=}")

        # get the version
        date_created = ds.GetMetadataItem("NC_GLOBAL#date_created")
        date_created_match = re.search(
            "\\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2}:\\d{2}", date_created
        )
        if date_created_match:
            version_datetime = datetime.fromisoformat(date_created_match[0]).replace(
                tzinfo=timezone.utc
            )
        else:
            filename = src_path.name
            date_str = re.search("\\d+", filename)[0]
            version_datetime = datetime.strptime(date_str, "%Y%m%d%H")

        for band in range(1, ds.RasterCount + 1):
            raster = ds.GetRasterBand(band)

            time_delta_str = raster.GetMetadataItem("NETCDF_DIM_time")
            time_delta = timedelta(minutes=int(time_delta_str))
            valid_datetime = since_time + time_delta

            nodata = raster.GetNoDataValue()

            cgdal.gdal_translate_w_options(
                tif := str(
                    dst_path / f'qtf.{valid_datetime.strftime("%Y%m%d_%H%M")}.tif'
                ),
                ds,
                bandList=[band],
                noData=nodata,
            )

            outfile_list.append(
                {
                    "filetype": acquirable,
                    "file": tif,
                    "datetime": valid_datetime.isoformat(),
                    "version": version_datetime.isoformat(),
                },
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
            logger.exception(f"{k}: {v}")

    finally:
        ds = None

    return outfile_list
