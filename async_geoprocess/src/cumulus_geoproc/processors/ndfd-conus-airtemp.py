"""NDFD CONUS Airtemp
"""


import os
import re
from datetime import datetime, timedelta, timezone
from string import Template

import pyplugs
from cumulus_geoproc import logger, utils
from cumulus_geoproc.configurations import CUMULUS_PRODUCTS_BASEKEY
from cumulus_geoproc.utils import cgdal
from osgeo import gdal

gdal.UseExceptions()

this = os.path.basename(__file__)


@pyplugs.register
def process(src: str, dst: str, acquirable: str = None):
    """Grid processor

    Parameters
    ----------
    src : str
        path to input file for processing
    dst : str
        path to temporary directory created from worker thread
    acquirable: str
        acquirable slug

    Returns
    -------
    List[dict]
        {
            "filetype": str,         Matching database acquirable
            "file": str,             Converted file
            "datetime": str,         Valid Time, ISO format with timezone
            "version": str           Reference Time (forecast), ISO format with timezone
        }
    """

    outfile_list = []

    try:
        filename = os.path.basename(src)
        filename_ = utils.file_extension(filename, ext="")

        filename_temp = Template("${filename}-${ymd}.tif")

        # Create a dictionary of time deltas and equivalent filetype
        f_type_dict = {
            3600: "ndfd-conus-airtemp-01h",
            10800: "ndfd-conus-airtemp-03h",
            21600: "ndfd-conus-airtemp-06h",
        }

        ds = gdal.Open("/vsis3_streaming/" + src)

        count = ds.RasterCount
        time_pattern = re.compile(r"\d+")
        tdelta2 = timedelta()

        for b in range(1, count + 1):
            try:
                tdelta1 = tdelta2

                raster = ds.GetRasterBand(b)

                valid_time_match = time_pattern.match(
                    raster.GetMetadataItem("GRIB_VALID_TIME")
                )
                vtime = datetime.fromtimestamp(int(valid_time_match[0]), timezone.utc)

                ref_time_match = time_pattern.match(
                    raster.GetMetadataItem("GRIB_REF_TIME")
                )
                rtime = datetime.fromtimestamp(int(ref_time_match[0]), timezone.utc)

                forcast_time_match = time_pattern.match(
                    raster.GetMetadataItem("GRIB_FORECAST_SECONDS")
                )
                forcast_time = float(forcast_time_match[0])

                # Check the time deltas to see if they are consistant
                tdelta2 = timedelta(seconds=forcast_time)
                tdelta = (tdelta2 - tdelta1).seconds  # Extract Band; Convert to COG

                if tdelta in f_type_dict:
                    translate_options = cgdal.gdal_translate_options(
                        bandList=[b], creationOptions=["TILED=YES", "COMPRESS=DEFLATE"]
                    )

                    _filename = filename_temp.substitute(
                        filename=filename_, ymd=vtime.strftime("%Y%m%d%H%M")
                    )
                    logger.debug(f"New Filename: {_filename}")

                    gdal.Translate(
                        temp_file := os.path.join(dst, _filename),
                        ds,
                        **translate_options,
                    )

                    outfile_list.append(
                        {
                            "filetype": f_type_dict[tdelta],
                            "file": temp_file,
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
