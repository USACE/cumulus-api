"""
# California Nevada River Forecast Center

## QPF 06 hour total precipitation
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

        # get the version
        date_created = ds.GetMetadataItem("NC_GLOBAL#creationTime")
        date_created_match = re.search("\\d+", date_created)
        if date_created_match:
            version_datetime = datetime.fromtimestamp(int(date_created_match[0])).replace(
                tzinfo=timezone.utc
            )
        else:
            filename = src_path.name
            date_str = re.search("\\d+_\\d+", filename)[0]
            version_datetime = datetime.strptime(date_str, "%Y%m%d_%H%M").replace(
                tzinfo=timezone.utc
            )

        # Get the subset metadata and the valid times as a list
        sub_meta = ds.GetMetadata_Dict()
        valid_times_list = list(eval(sub_meta[f"{SUBSET_NAME}#validTimes"]))
        valid_times_list.sort()

        for i, t in enumerate(valid_times_list):
            # skip the zero valid time
            if i == 0:
                continue

            valid_datetime = datetime.fromtimestamp(t).replace(tzinfo=timezone.utc)

            raster_band = ds.GetRasterBand(i)

            nodata = raster_band.GetNoDataValue()

            cgdal.gdal_translate_w_options(
                tif := str(
                    dst_path / f'qpf.{valid_datetime.strftime("%Y%m%d_%H%M")}.tif'
                ),
                ds,
                bandList=[i],
                noData=nodata,
            )

            # validate COG
            if (validate := cgdal.validate_cog("-q", tif)) == 0:
                logger.debug(f"Validate COG = {validate}\t{tif} is a COG")

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
            logger.error(f"{k}: {v}")

    finally:
        ds = None

    return outfile_list
