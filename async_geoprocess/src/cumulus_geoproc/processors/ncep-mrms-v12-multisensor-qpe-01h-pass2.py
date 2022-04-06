"""MRMS MultiSensor QPE 01H Pass1
"""


import os
import re
from datetime import datetime, timezone
from tempfile import TemporaryDirectory

import pyplugs
from cumulus_geoproc import logger, utils
from cumulus_geoproc.configurations import CUMULUS_PRODUCTS_BASEKEY
from cumulus_geoproc.utils import boto, cgdal
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
    grib_element = "MultiSensor_QPE_01H_Pass2"

    outfile_list = list()

    filename = os.path.basename(src)
    filename_ = utils.file_extension(filename)

    try:
        bucket, key = src.split("/", maxsplit=1)
        logger.debug(f"s3_download_file({bucket=}, {key=})")

        tmp_dir = TemporaryDirectory(dir=dst)
        src_ = boto.s3_download_file(bucket=bucket, key=key, dst=tmp_dir.name)
        logger.debug(f"S3 Downloaded File: {src_}")

        ds = gdal.Open("/vsigzip/" + src_)
        fileinfo = gdal.Info(ds, format="json")
        bands = fileinfo["bands"]

        logger.debug(f"File Info: {fileinfo}")

        # figure out the band number
        band_number = [
            b["band"]
            for b in bands
            if b["metadata"][""]["GRIB_ELEMENT"] == grib_element
        ][-1]

        raster = ds.GetRasterBand(band_number)
        meta = raster.GetMetadata_Dict()
        valid_time = meta["GRIB_VALID_TIME"]

        # Get Datetime from String Like "1599008400 sec UTC"
        time_pattern = re.compile(r"\d+")
        valid_time_match = time_pattern.match(valid_time)
        dt_valid = datetime.fromtimestamp(int(valid_time_match[0]), timezone.utc)

        # Extract Band; Convert to COG
        translate_options = cgdal.gdal_translate_options()
        gdal.Translate(
            temp_file := os.path.join(dst, filename_),
            raster.GetDataset(),
            **translate_options,
        )

        # closing the data source
        ds = None
        raster = None

        outfile_list = [
            {
                "filetype": acquirable,
                "file": temp_file,
                "datetime": dt_valid.isoformat(),
                "version": None,
            },
        ]

    except RuntimeError as ex:
        logger.error(f"{type(ex).__name__}: {this}: {ex}")
    except KeyError as ex:
        logger.error(f"{type(ex).__name__}: {this}: {ex}")
    except IndexError as ex:
        logger.error(f"IndexError: {__name__}: {ex}")

    return outfile_list
