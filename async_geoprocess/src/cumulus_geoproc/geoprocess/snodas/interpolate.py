"""SNODAS interpolation
"""

import asyncio
import os
from collections import namedtuple
from datetime import datetime, timezone
from string import Template

import pkg_resources
from cumulus_geoproc import logger
from cumulus_geoproc.configurations import CUMULUS_PRODUCTS_BASEKEY
from cumulus_geoproc.geoprocess.snodas import no_data_value, product_code
from cumulus_geoproc.utils import boto, cgdal, file_extension
from osgeo import gdal

gdal.UseExceptions()

this = os.path.basename(__file__)


def is_lakefix(dt: datetime, code: str):
    """Determine if needing 'lakefix'

    Parameters
    ----------
    dt : datetime
        datetime object
    code : str
        parameter code related to SNODAS parameters

    Returns
    -------
    bool
        True | False if needing 'lakefix'
    """
    codes = ("1034", "1036")
    dt_after = datetime(2014, 10, 9, 0, 0, tzinfo=timezone.utc)
    if dt >= dt_after and code in codes:
        return True
    else:
        return False


async def snodas_interp_task(
    filepath: str,
    product: str,
    dt: datetime,
    max_dist: str,
    nodata: str,
    lakefix: bool = False,
):
    """SNODAS interpolation task method used with asyncio

    Parameters
    ----------
    filepath : str
        FQPN to processed SNODAS COG
    product : str
        Cumulus product name
    dt : datetime
        datetime object
    max_dist : str
        maximum distance in pixel for gdal_fillnodata
    nodata : str
        raster no data value
    lakefix : bool, optional
        determine if product needs 'lakefix', by default False

    Returns
    -------
    dict[str, str] | None
        Dictionary of attributes needed to upload to S3 or None
    """
    try:
        dst, filename = os.path.split(filepath)
        ds = gdal.Open(filepath, gdal.GA_ReadOnly)
        meta_data = ds.GetRasterBand(1).GetMetadata()
        ds = None

        if lakefix:
            # get the no data masking raster
            masking_raster = pkg_resources.resource_filename(
                __package__, "data/no_data_areas_swe_20140201.tif"
            )
            lakefix_tif = os.path.join(
                dst,
                file_extension(filename, suffix=".tiff"),
            )
            # set zeros as no data (-9999)
            cgdal.gdal_calculate(
                "-A",
                filepath,
                "-B",
                masking_raster,
                "--outfile",
                lakefix_tif,
                "--calc",
                f"numpy.where((A == 0) & (B == {nodata}), {nodata}, A)",
                "--NoDataValue",
                nodata,
                "--quiet",
            )
            filepath = lakefix_tif

        # the following creation options (-co) are defaulted if driver is COG
        # -of GTiff required here because COG has no Create(); therefore GTiff
        # driver used with creationOptions to be COG
        dst_tif = os.path.join(
            dst, file_extension(filename, suffix="-interpolated.tif")
        )
        cgdal.gdal_fillnodataval(
            "-q",
            "-md",
            str(max_dist),
            filepath,
            "-of",
            "GTiff",
            dst_tif,
            "-co",
            "COMPRESS=LZW",
            "-co",
            "COPY_SRC_OVERVIEWS=YES",
            "-co",
            "TILE=YES",
            "-co",
            "NUM_THREADS=ALL_CPUS",
        )

        ds = gdal.Open(dst_tif)
        ds.GetRasterBand(1).SetMetadata(meta_data)
        ds = None

        return {
            "file": dst_tif,
            "filetype": product,
            "datetime": dt.isoformat(),
            "version": None,
        }

    except (RuntimeError, KeyError, Exception) as ex:
        logger.error(f"{type(ex).__name__}: {this}: {ex}")
    finally:
        ds = None


async def snodas(cfg: namedtuple, dst: str):
    """Main method building asyncio tasks

    Parameters
    ----------
    cfg : namedtuple
        namedtuple with SQS message as attributes
    dst : str
        FQPN to temporary directory

    Returns
    -------
    List[dict[str, str]]
        List of dictionary objects with attributes needed to upload to S3
    """
    tasks = []
    dt = (
        datetime.strptime(cfg.datetime, "%Y%m%d")
        .replace(hour=6)
        .replace(tzinfo=timezone.utc)
    )
    nodata_value = no_data_value(dt)
    for code in ("1034", "1036", "1038", "3333", "2072"):
        filename = Template.substitute(
            product_code[code]["file_template"], YMD=cfg.datetime
        )
        product = product_code[code]["product"] + "-interpolated"
        key = (
            CUMULUS_PRODUCTS_BASEKEY
            + "/"
            + product_code[code]["product"]
            + "/"
            + filename
        )
        lakefix = is_lakefix(
            dt,
            code,
        )

        if download_file := boto.s3_download_file(cfg.bucket, key, dst=dst):
            tasks.append(
                asyncio.create_task(
                    snodas_interp_task(
                        download_file,
                        product,
                        dt,
                        cfg.max_distance,
                        nodata_value,
                        lakefix,
                    )
                )
            )

    # return the list of objects that are not None
    return_objs = []
    for task in tasks:
        result = await task
        if result is not None:
            return_objs.append(result)

    return return_objs


if __name__ == "__main__":
    pass
