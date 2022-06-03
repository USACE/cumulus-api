"""_summary_
"""

import os
import subprocess
from collections import namedtuple

import cumulus_packager
import pyplugs
from cumulus_packager import logger
from cumulus_packager.packager import PACKAGE_STATUS
from osgeo import gdal

gdal.UseExceptions()

this = os.path.basename(__file__)

_status = lambda x: PACKAGE_STATUS[int(x)]


@pyplugs.register
def writer(
    id: str,
    outkey: str,
    extent: dict,
    src: list,
    dst: str,
    cellsize: float,
    dst_srs: str = "EPSG:5070",
    callback=None,
):
    # return None if no items in the 'contents'
    if len(src) < 1:
        callback(id, _status(-1))
        return

    _cumulus_packager = os.path.dirname(cumulus_packager.__file__)
    _extent_name = extent["name"]
    _bbox = extent["bbox"]
    _progress = 0

    try:
        for idx, tif in enumerate(src):
            TifCfg = namedtuple("TifCfg", tif)(**tif)

            filename_ = os.path.basename(TifCfg.key)
            dsspathname = f"/SHG/{_extent_name}/{TifCfg.dss_cpart}/{TifCfg.dss_dpart}/{TifCfg.dss_epart}/{TifCfg.dss_fpart}/"

            ds = gdal.Open(f"/vsis3_streaming/{TifCfg.bucket}/{TifCfg.key}")

            # GDAL Warp the Tiff to what we need for DSS
            gdal.Warp(
                tmptiff := os.path.join(dst, filename_),
                ds,
                format="GTiff",
                outputBounds=_bbox,
                xRes=cellsize,
                yRes=cellsize,
                targetAlignedPixels=True,
                dstSRS=dst_srs,
                outputType=gdal.GDT_Float64,
                resampleAlg="bilinear",
                dstNodata=-9999,
                copyMetadata=False,
            )

            # as a subprocess
            tmpdss = os.path.join(dst, id + ".dss")
            cmd = os.path.join(_cumulus_packager, "bin/tiffdss")
            cmd += " " + tmptiff
            cmd += " " + tmpdss
            cmd += f' "{dsspathname}"'
            cmd += " shg-time"
            cmd += " " + TifCfg.dss_datatype
            cmd += " " + TifCfg.dss_unit
            cmd += " gmt"
            cmd += " zlib"

            sp = subprocess.Popen(
                cmd,
                cwd=_cumulus_packager,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            try:
                outs, errs = sp.communicate(timeout=15)
            except subprocess.TimeoutExpired:
                sp.kill()
                outs, errs = sp.communicate()

            logger.debug(f"STDOUT: {outs}")
            logger.debug(f"STDERR: {errs}")

            # callback
            _progress = round(idx / len(src), 2)
            logger.debug(f"Progress: {_progress}")

            if callback is not None:
                callback(id, _status(_progress), _progress)

    except (RuntimeError, Exception) as ex:
        logger.error(f"{type(ex).__name__}: {this}: {ex}")
        callback(id, _status(-1), _progress)
    finally:
        ds = None

    return tmpdss


if __name__ == "__main__":
    pass
