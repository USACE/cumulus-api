"""Cumulus specific gdal utilities
"""

import os

from cumulus_geoproc import logger
from osgeo import gdal
from osgeo_utils import gdal_calc

gdal.UseExceptions()

this = os.path.basename(__file__)


def gdal_translate_options(**kwargs):
    """Return gdal translate options

    Returns
    -------
    dict
        dictionary of gdal translate options with base options
    """
    base = {
        "format": "GTiff",
        "creationOptions": ["TILED=YES", "COPY_SRC_OVERVIEWS=YES", "COMPRESS=DEFLATE"],
    }
    return {**base, **kwargs}


# get a band based on provided attributes in the metadata
def find_band(data_set: "gdal.Dataset", attr: dict = {}):
    """Return the band number

    Parameters
    ----------
    data_set : gdal.Dataset
        gdal dataset
    attr : dict, optional
        attributes matching those in the metadata, by default {}

    Returns
    -------
    int
        band number
    """
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
        finally:
            raster = None

    return None


def gdal_calculate(*args):
    """Implement gdal-utils gdal_calc CLI utility"""
    argv = [gdal_calc.__file__]
    argv.extend(list(args))

    logger.debug(f"Argvs: {argv=}")

    gdal_calc.main(argv)


# TODO: GridProcess class
class GridProcess:
    pass
