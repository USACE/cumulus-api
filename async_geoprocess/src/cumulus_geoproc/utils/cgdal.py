"""Cumulus specific gdal utilities
"""

import os
from osgeo import gdal

from cumulus_geoproc import logger

gdal.UseExceptions()

this = os.path.basename(__file__)


def gdal_translate_options(**kwargs):
    base = {
        "format": "GTiff",
        "creationOptions": ["TILED=YES", "COPY_SRC_OVERVIEWS=YES", "COMPRESS=DEFLATE"],
    }
    return {**base, **kwargs}


# TODO: create a generator to support reading grid metadata

# get a band based on provided attributes in the metadata
def find_band(data_set: "gdal.Dataset", attr: dict = {}):
    count = data_set.RasterCount
    for b in range(1, count + 1):
        try:
            raster = data_set.GetRasterBand(b)
            meta = raster.GetMetadata_Dict()
            has_attr = [
                True
                for key, val in attr.items()
                if (key in meta and val == raster.GetMetadataItem(key))
            ]
            if len(has_attr) == len(attr):
                logger.debug(f"{has_attr=}")
                return b

        except RuntimeError as ex:
            logger.error(f"{type(ex).__name__}: {this}: {ex}")
            continue

    return None


# TODO: GridProcess class
class GridProcess:
    pass
