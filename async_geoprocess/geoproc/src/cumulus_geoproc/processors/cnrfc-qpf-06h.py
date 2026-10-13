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
from cumulus_geoproc.utils import cgdal, hrap

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

        # NOTE: Because we are already working against a copy of the acquirable file 'src',
        #       not the original archive file on AWS S3, use gdal.Open() with gdal.GA_Update
        #       (not gdal.GA_ReadOnly).
        #
        #       This allows setting Transform and Projection on the dataset so they are included
        #       in the bands that get translated out. Because 'src' is already a copy, no risk of
        #       corrupting the original file at this time. If 'src' is ever passed as a virtual 
        #       path to the original file in archive (e.g. /vsis3/...), will want to revisit.
        try:
            ds = gdal.Open("/vsigzip/" + src, gdal.GA_Update)
        except RuntimeError as err:
            logger.warning(err)
            logger.warning(f'gunzip "{src}" and use as source file')
            src_unzip = utils.decompress(src, str(dst_path))
            ds = gdal.Open(src_unzip, gdal.GA_Update)

        subdatasets = ds.GetSubDatasets()

        for subdataset in subdatasets:
            subsetpath, datatype = subdataset
            if SUBSET_NAME in datatype and SUBSET_DATATYPE in datatype:
                ds = gdal.Open(subsetpath, gdal.GA_Update)
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
            version_datetime = datetime.fromtimestamp(
                int(date_created_match[0])
            ).replace(tzinfo=timezone.utc)
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

        # Initial metadata value for qpe_grid#latLonLL looks like: "{-123.6735229012065,29.94159256439344}"
        # strip() removes characters "{" and "}"
        # split() returns a list of two strings (which represent numbers), split on the ","
        # map() converts each string to a float; list() converts the map object back to a list
        #
        # lower left coordinates (minimum x, minimum y)
        lonLL, latLL = list(map(float, sub_meta[f"{SUBSET_NAME}#latLonLL"].strip('{}').split(','))) # Lon/Lat
        hrap_xmin, hrap_ymin = list(map(float, sub_meta[f"{SUBSET_NAME}#gridPointLL"].strip('{}').split(','))) # HRAP
        ster_xmin, ster_ymin = hrap.ster_x(hrap_xmin), hrap.ster_y(hrap_ymin) # Polar Stereographic

        #
        # upper right coordinates (maximum x, maximum y) in geographic space and pixel space
        lonUR, latUR = list(map(float, sub_meta[f"{SUBSET_NAME}#latLonUR"].strip('{}').split(','))) # Lon/Lat
        hrap_xmax, hrap_ymax = list(map(float, sub_meta[f"{SUBSET_NAME}#gridPointUR"].strip('{}').split(','))) # HRAP
        ster_xmax, ster_ymax = hrap.ster_x(hrap_xmax), hrap.ster_y(hrap_ymax) # Polar Stereographic
        #
        # size of the grid
        # nrows = number of rows in the grid (y or latitude direction)
        # ncols = number of columns in the grid (x or longitude direction)
        ncols, nrows = list(map(float, sub_meta[f"{SUBSET_NAME}#domainExtent"].strip('{}').split(',')))

        # Grid Cell Resolution; polar stereographic reference
        xres = (ster_xmax - ster_xmin) / float(ncols)
        yres = (ster_ymax - ster_ymin) / float(nrows)

        # Specify geotransform
        # https://gdal.org/tutorials/geotransforms_tut.html#introduction-to-geotransforms
        # GT(0) x-coordinate of the upper-left corner of the upper-left pixel.
        # GT(1) w-e pixel resolution / pixel width.
        # GT(2) row rotation (typically zero).
        # GT(3) y-coordinate of the upper-left corner of the upper-left pixel.
        # GT(4) column rotation (typically zero).
        # GT(5) n-s pixel resolution / pixel height (negative value for a north-up image).
        geotransform = (ster_xmin, xres, 0, ster_ymax, 0, -yres)

        ds.SetGeoTransform(geotransform)
        ds.SetProjection(hrap.PROJ4)

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
                outputBounds=[lonLL, latUR, lonUR, latLL],
                outputSRS="EPSG:4326",
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
