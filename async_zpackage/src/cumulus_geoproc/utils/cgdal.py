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
import pathlib
import subprocess
from typing import List

from cumulus_geoproc import logger
from osgeo import gdal
from osgeo_utils import gdal_calc
from osgeo_utils.samples import validate_cloud_optimized_geotiff

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
    }
    return {**base, **kwargs}


def gdal_translate_w_overviews(
    dst: str,
    src: gdal.Dataset,
    translate_options: dict,
    resampling: str = None,
    overviewlist: List[int] = [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048],
):
    """Build overviews for the gdal dataset with the resampling algorithm provided

    If no sampling algorithm is given, only gdal.Translate() executed

    allowable resampling algorithms:
        nearest,average,rms,bilinear,gauss,cubic,cubicspline,lanczos,average_magphase,mode

    Parameters
    ----------
    dst : str
        Output dataset name
    src : gdal.Dataset
        Dataset object or a filename
    translate_options : dict
        Dictionary of creation options
    resampling : str, optional
        resampling algorithm, by default None
    overviewlist : List[int], optional
        list of integers, by default [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048]
    """

    resampling_algo = (
        "nearest",
        "average",
        "rms",
        "bilinear",
        "gauss",
        "cubic",
        "cubicspline",
        "lanczos",
        "average_magphase",
        "mode",
    )
    if resampling is not None and resampling not in resampling_algo:
        logger.debug(f"Resampling algorithm {resampling} not available")
        return False
    try:
        if resampling:
            gdal.Translate(
                f"/vsimem/{dst}",
                src,
                format="GTiff",
                creationOptions=[
                    "COMPRESS=LZW",
                    "TILED=YES",
                ],
            )
            _ds = gdal.Open(f"/vsimem/{dst}", gdal.GA_Update)
            _ds.BuildOverviews(resampling=resampling, overviewlist=overviewlist)
            gdal.Translate(
                dst,
                _ds,
                **translate_options,
            )
        else:
            gdal.Translate(
                dst,
                src,
                **translate_options,
            )
        return True
    except RuntimeError as ex:
        logger.error(f"{type(ex).__name__}: {this}: {ex}")
    finally:
        _ds = None
    return False


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


def gdal_fillnodataval(src: str, dst: str, /, *args):
    """Implement gdal-utils gdal_fillnodata CLI utility as a subprocess

    gdal_fillnodata documentation:

    https://gdal.org/programs/gdal_fillnodata.html
    """
    argv = ["gdal_fillnodata.py"]
    argv.extend(list(args))
    argv.append(src)
    argv.append(dst)

    logger.debug(f"Argvs: {argv=}")

    try:
        result = subprocess.check_call(argv, cwd=pathlib.PurePath(src).parent)
        return result
    except subprocess.CalledProcessError as ex:
        logger.error(f"{type(ex).__name__}: {this}: {ex}")
        return result


def validate_cog(*args):
    argv = [validate_cloud_optimized_geotiff.__file__]
    argv.extend(list(args))

    logger.debug(f"Argvs: {argv=}")

    return validate_cloud_optimized_geotiff.main(argv)


# TODO: GridProcess class
class GridProcess:
    pass


if __name__ == "__main__":
    pass
