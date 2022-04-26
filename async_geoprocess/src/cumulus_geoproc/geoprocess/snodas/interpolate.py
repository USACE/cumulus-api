"""_summary_
"""

import asyncio
import importlib
import os
from collections import namedtuple
from datetime import datetime, timezone
from string import Template

from cumulus_geoproc.configurations import CUMULUS_PRODUCTS_BASEKEY
from cumulus_geoproc.geoprocess.snodas import no_data_value, product_code
from cumulus_geoproc.utils import boto, cgdal, file_extension


def is_lakefix(dt: datetime, code: str):
    codes = ("1034", "1036")
    dt_after = datetime(2014, 10, 9, 0, 0, tzinfo=timezone.utc)
    if dt >= dt_after and code in codes:
        return True
    else:
        return False


async def snodas_interp_task(
    filename: str,
    bucket: str,
    key: str,
    dst: str,
    max_dist: str,
    nodata: str,
    lakefix: bool = False,
):
    if download_file := boto.s3_download_file(bucket, key, dst=dst):
        dst_file = os.path.join(
            dst, file_extension(filename, suffix="-interpolate.tif")
        )
        if lakefix:
            # get the no data masking raster
            masking_raster = importlib.resources.path(
                __package__, "data/no_data_areas_swe_20140201.tif"
            )
            lakefix_tif = os.path.join(
                dst,
                file_extension(filename, suffix=".tiff"),
            )
            # set zeros as no data (-9999)
            cgdal.gdal_calculate(
                "-A",
                download_file,
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
            download_file = lakefix_tif

        cgdal.gdal_fillnodataval(
            "-q",
            "-md",
            max_dist,
            download_file,
            "-of",
            "COG",
            dst_file,
        )


async def snodas(cfg: namedtuple, dst: str):
    tasks = []
    dt = datetime.strptime(cfg.datetime, "%Y%m%d").replace(tzinfo=timezone.utc)
    nodata_value = no_data_value(dt)
    for code in ("1034", "1036", "1038", "2072", "3333"):
        filename = Template.substitute(
            product_code[code]["file_template"], YMD=cfg.datetime
        )
        key = (
            CUMULUS_PRODUCTS_BASEKEY
            + "/"
            + product_code[code]["product"]
            + "/"
            + filename
        )
        lakefix = is_lakefix(
            datetime.strptime(cfg.datetime, "%Y%m%d").replace(tzinfo=timezone.utc),
            code,
        )
        tasks.append(
            asyncio.create_task(
                snodas_interp_task(
                    filename,
                    cfg.bucket,
                    key,
                    dst,
                    cfg.max_distance,
                    nodata_value,
                    lakefix,
                )
            )
        )

    for task in tasks:
        await task


if __name__ == "__main__":
    pass
