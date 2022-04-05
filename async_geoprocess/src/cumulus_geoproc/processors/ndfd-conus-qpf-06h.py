"""NDFD CONUS QPF 6 hour
"""


import os
import re
from datetime import datetime, timezone

import pyplugs
from cumulus_geoproc import logger, utils
from cumulus_geoproc.configurations import CUMULUS_PRODUCTS_BASEKEY
from cumulus_geoproc.utils import cgdal
from osgeo import gdal

gdal.UseExceptions()


def bands(bands: "list[dict]"):
    """Generator for bands in the gdalinfo list of dictionary objects

    Parameters
    ----------
    bands : list[dict]
        list of dictionaries describing each raster band

    Yields
    ------
    tuple
        band_number: int, reference_time: datetime and valid_time: datetime
    """

    time_pattern = re.compile(r"\d+")
    for band in bands:
        band_number = band["band"]
        raster_band = gdal.GetRasterBand(band_number)

        metadata_dict = raster_band.GetMetadata_Dict()

        valid_time_match = time_pattern.match(metadata_dict["GRIB_VALID_TIME"])
        ref_time_match = time_pattern.match(metadata_dict["GRIB_REF_TIME"])

        ref_time = datetime.fromtimestamp(int(valid_time_match[0]), timezone.utc)
        valid_time = datetime.fromtimestamp(int(ref_time_match[0]), timezone.utc)

        yield (band_number, ref_time, valid_time)


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

    outfile_list = list()

    filename = os.path.basename(src)
    filename_ = utils.file_extension(filename, ext="")

    try:
        ds = gdal.Open("/vsis3_streaming" + src)

        fileinfo = gdal.Info(ds, format="json")

        # Create the tif files based on the list of dictionaries from above
        for i, band in enumerate(bands(fileinfo["bands"])):
            try:
                bandn, rtime, vtime, tdelta = band

                # Extract Band; Convert to COG
                translate_options = cgdal.gdal_translate_options(bandList=[bandn])

                _filename = f"{filename_}-{vtime.strftime('%Y%m%d%H%M').tif}"

                gdal.Translate(
                    temp_file := os.path.join(dst, _filename),
                    ds,
                    **translate_options,
                )

                outfile_list.append(
                    {
                        "filetype": "ndfd-conus-qpf-06h",
                        "file": temp_file,
                        "datetime": vtime.isoformat(),
                        "version": rtime.isoformat(),
                    }
                )
            except RuntimeError as ex:
                logger.error(f"RuntimeError: {os.path.basename(__file__)}: {ex}")
                continue

    except RuntimeError as ex:
        logger.error(f"RuntimeError: {os.path.basename(__file__)}: {ex}")
    except KeyError as ex:
        logger.error(f"KeyError: {os.path.basename(__file__)}: {ex}")

    return outfile_list
