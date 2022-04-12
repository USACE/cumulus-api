"""NOHRSC SNODAS Unmasked
"""

import os
import re
from datetime import datetime, timedelta

import pyplugs
from cumulus_geoproc import logger, utils
from cumulus_geoproc.geoprocess.snodas import (
    BOUNDING_DATE,
    utils,
    translate_options as snodas_translate_options,
    product_code as snodas_product_code,
)
from cumulus_geoproc.geoprocess.snodas import handler
from cumulus_geoproc.utils import cgdal, file_extension
from osgeo import gdal

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

    paramater_codes = [1034, 1036, 1038, 1044]

    try:
        # decompress the tar and gzip files in the tar
        decompressed_files = utils.decompress(src, dst, recursive=True)
        if not os.path.isdir(decompressed_files):
            raise Exception(f"Not a directory: {decompressed_files}")

        # generator for only the files ending with .dat
        dat_files = (f for f in os.listdir(decompressed_files) if f.endswith(".dat"))

        translate_to_tif = {}
        # create tif files for only the files needed
        for file_ in dat_files:
            dat_file_path = os.path.join(decompressed_files, file_)
            snodas_file = utils.SnodasFilenameParse(file_)
            snodas_file_product = snodas_file.product
            if snodas_file_product in paramater_codes:
                region = snodas_file.region

                # True (1) or False (0) determines which output bounds to use
                output_bounds = snodas_translate_options[region]["translate_option"][
                    (snodas_file.date_time >= BOUNDING_DATE)
                ]
                # Hdr text to write
                hdr_ = snodas_translate_options[region]["hdr"]
                with open(hdr_file := dat_file_path.replace(".dat", ".hdr")) as fh:
                    fh.write(hdr_)
                # add the kwargs to the translate options
                options_ = snodas_translate_options["global"]
                translate_options = cgdal.gdal_translate_options(
                    creationOptions=None, **options_, **output_bounds
                )
                ds = gdal.Open(dat_file_path, gdal.GA_ReadOnly)
                gdal.Translate(
                    tif_file := dat_file_path.replace(".dat", ".tif"),
                    ds,
                    **translate_options,
                )
                ds = None

                if snodas_file_product == 1044:
                    snodas_file_product = 3333
                    tif_file_shift = tif_file
                    cgdal.gdal_calculate(
                        "-A",
                        tif_file_shift,
                        "--outfile",
                        tif_file := tif_file_shift.replace("1044", "3333"),
                        "--calc",
                        "A*100",
                    )

                translate_to_tif[snodas_file_product] = {
                    "file": tif_file,
                    "filetype": snodas_product_code[snodas_file_product]["product"],
                    "datetime": snodas_file.date_time.isoformat(),
                    "version": None,
                }

        # cold content = swe * 2114 * snowtemp (degc) / 333000
        translate_to_tif.update(handler.cold_content(translate_to_tif))

        outfile_list.extend(list(translate_to_tif.values()))

    except (RuntimeError, KeyError, Exception) as ex:
        logger.error(f"{type(ex).__name__}: {this}: {ex}")
    finally:
        ds = None

    return outfile_list
