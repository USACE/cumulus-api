"""
# California Nevada River Forecast Center

## QPE 06 hour total precipitation
"""


import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import pyplugs
from osgeo import gdal

from cumulus_geoproc import logger, utils
from cumulus_geoproc.utils import cgdal, hrap

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

    try:
        # Source and Destination as Paths
        # take the source path as the destination unless defined.
        src_path = Path(src)
        if dst is None:
            dst_path = src_path.parent
        else:
            dst_path = Path(dst)

        # change the suffix
        filename_tif = src_path.with_suffix(".tif")
        if (
            len(src_path.suffixes) >= 2
        ):  # 2 or more suffixes assumes pattern like *.tar.gz, *.nc.gz, *.grb.gz, etc
            filename_tif = Path(src_path.stem).with_suffix(".tif")

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

        dataset_meta = gdal.Info(ds, format="json")

        # Get Geotransform Information
        m = dataset_meta["metadata"][""]

        # Initial metadata value for qpe_grid#latLonLL looks like: "{-123.6735229012065,29.94159256439344}"
        # strip() removes characters "{" and "}"
        # split() returns a list of two strings (which represent numbers), split on the ","
        # map() converts each string to a float; list() converts the map object back to a list
        #
        # lower left coordinates (minimum x, minimum y)
        lonLL, latLL = list(map(float, m["qpe_grid#latLonLL"].strip('{}').split(','))) # Lon/Lat
        hrap_xmin, hrap_ymin = list(map(float, m["qpe_grid#gridPointLL"].strip('{}').split(','))) # HRAP
        ster_xmin, ster_ymin = hrap.ster_x(hrap_xmin), hrap.ster_y(hrap_ymin) # Polar Stereographic

        #
        # upper right coordinates (maximum x, maximum y) in geographic space and pixel space
        lonUR, latUR = list(map(float, m["qpe_grid#latLonUR"].strip('{}').split(','))) # Lon/Lat
        hrap_xmax, hrap_ymax = list(map(float, m["qpe_grid#gridPointUR"].strip('{}').split(','))) # HRAP
        ster_xmax, ster_ymax = hrap.ster_x(hrap_xmax), hrap.ster_y(hrap_ymax) # Polar Stereographic
        #
        # size of the grid
        # nrows = number of rows in the grid (y or latitude direction)
        # ncols = number of columns in the grid (x or longitude direction)
        ncols, nrows = list(map(float, m["qpe_grid#domainExtent"].strip('{}').split(',')))

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
        
        bands = dataset_meta["bands"]
        for band in bands:
            band_num = band["band"]
            band_meta = band["metadata"][""]

            # validTimes is a str with {} and can be eval() to set()
            valid_times = eval(band_meta["validTimes"])
            t1, t2 = valid_times
            valid_datetime = datetime.fromtimestamp(t2).replace(tzinfo=timezone.utc)

            raster_band = ds.GetRasterBand(band_num)
            nodata = raster_band.GetNoDataValue()

            cgdal.gdal_translate_w_options(
                tif := str(dst_path / filename_tif),
                ds,
                outputBounds=[lonLL, latUR, lonUR, latLL],
                outputSRS="EPSG:4326",
                bandList=[band_num],
                noData=nodata,
            )

            # validate COG
            if (validate := cgdal.validate_cog("-q", tif)) == 0:
                logger.debug(f"Validate COG = {validate}\t{tif} is a COG")

            outfile_list = [
                {
                    "filetype": acquirable,
                    "file": tif,
                    "datetime": valid_datetime.isoformat(),
                    "version": None,
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
    return outfile_list
