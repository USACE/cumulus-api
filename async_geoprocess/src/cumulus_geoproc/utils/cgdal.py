"""Cumulus specific gdal utilities

    GTiff Creation Options to be a COG:
        "-co",
        "COMPRESS=LZW",
        "-co",
        "COPY_SRC_OVERVIEWS=YES",
        "-co",
        "TILE=YES",
"""

import os

from cumulus_geoproc import logger
from osgeo import gdal
from osgeo_utils import gdal_calc, gdal_fillnodata

gdal.UseExceptions()

this = os.path.basename(__file__)


def gdal_translate_options(**kwargs):
    """Return gdal translate options

    Add dictionary attributes to use those options for translate

    Adding an existing attribute in 'base' will overwright that option

    Returns
    -------
    dict
        dictionary of gdal translate options with base option(s)

    base = {
        "format": "COG",
    }
    """
    # COG driver generates overviews while GTiff uses seperate step to build them
    base = {
        "format": "COG",
        "creationOptions": ["OVERVIEWS=IGNORE_EXISTING"],
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
                if (key in meta and val in raster.GetMetadataItem(key))
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
    """Implement gdal-utils gdal_calc CLI utility

    gdal_translate documentation:

    https://gdal.org/programs/gdal_translate.html
    """
    argv = [gdal_calc.__file__]
    argv.extend(list(args))

    logger.debug(f"Argvs: {argv=}")

    gdal_calc.main(argv)


def gdal_fillnodataval(*args):
    """Implement gdal-utils gdal_fillnodata CLI utility

    gdal_fillnodata documentation:

    https://gdal.org/programs/gdal_fillnodata.html
    """
    argv = [gdal_calc.__file__]
    argv.extend(list(args))

    logger.debug(f"Argvs: {argv=}")

    gdal_fillnodata.main(argv)


# TODO: GridProcess class
class GridProcess:
    pass
