"""Packager writer plugin

    COG --> DSS7
"""
import os
import subprocess
import time
from collections import namedtuple
from ctypes import (
    CDLL,
    LibraryLoader,
    addressof,
    c_char_p,
    c_int,
    c_long,
    c_longlong,
    memset,
    sizeof,
)

import cumulus_packager
import pyplugs
from cumulus_packager import logger
from cumulus_packager.packager import PACKAGE_STATUS
from osgeo import gdal

# _cumulus_packager = os.path.dirname(cumulus_packager.__file__)
c_tiffdss = LibraryLoader(CDLL).LoadLibrary("libtiffdss.so")

write_record = c_tiffdss.writeRecord
zopen = c_tiffdss.open
zclose = c_tiffdss.close

write_record.argtypes = (
    c_longlong,
    c_char_p,
    c_char_p,
    c_char_p,
    c_char_p,
    c_char_p,
    c_char_p,
    c_char_p,
    c_char_p,
)
write_record.restype = c_int

zopen.argtypes = [c_longlong, c_char_p]
zopen.restype = c_int
zclose.argtypes = [c_longlong]
zclose.restype = c_int


gdal.UseExceptions()

this = os.path.basename(__file__)

_status = lambda x: PACKAGE_STATUS[int(x)]


@pyplugs.register
def writer(
    id: str,
    extent: dict,
    src: list,
    dst: str,
    cellsize: float,
    dst_srs: str = "EPSG:5070",
    callback=None,
):
    """Packager writer plugin

    Parameters
    ----------
    id : str
        Download ID
    extent : dict
        Object with watershed name and bounding box
    src : list
        List of objects describing the GeoTiff (COG)
    dst : str
        Temporary directory
    cellsize : float
        Grid resolution
    dst_srs : str, optional
        Destination Spacial Reference, by default "EPSG:5070"
    callback : callable, optional
        callback function sending message to the DB, by default None, by default None

    Returns
    -------
    str
        FQPN to dss file
    """
    start = time.perf_counter()
    # return None if no items in the 'contents'
    if len(src) < 1:
        callback(id, _status(-1))
        return

    _extent_name = extent["name"]
    _bbox = extent["bbox"]
    _progress = 0

    # this can go away when the payload has the resolution
    cellsize = 2000 if cellsize is None else None
    ifltab = c_longlong(250)
    memset(addressof(ifltab), 0, 250 * sizeof(c_long))

    try:
        tmpdss = os.path.join(dst, id + ".dss")
        ret = zopen(addressof(ifltab), c_char_p(str.encode(tmpdss)))
        logger.debug(f"zopen returned: {ret}")
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
            # tmpdss = os.path.join(dst, id + ".dss")
            # cmd = os.path.join(_cumulus_packager, "bin/tiffdss")
            # cmd += f' "{tmptiff}"'
            # cmd += f' "{tmpdss}"'
            # cmd += f' "{dsspathname}"'
            # cmd += " shg-time"
            # cmd += f' "{TifCfg.dss_datatype}"'
            # cmd += f' "{TifCfg.dss_unit}"'
            # cmd += " gmt"
            # cmd += " zlib"

            try:
                substart = time.perf_counter()
                ret = write_record(
                    addressof(ifltab),
                    tmptiff.encode(),
                    tmpdss.encode(),
                    dsspathname.encode(),
                    b"shg-time",
                    str.encode(TifCfg.dss_datatype),
                    str.encode(TifCfg.dss_unit),
                    b"gmt",
                    b"zlib",
                )
                logger.debug(
                    f"Subprocessor Perfomance Counter: {time.perf_counter() - substart}"
                )
                # callback
                _progress = idx / len(src)
                logger.debug(f"Progress: {_progress}")

                if callback is not None:
                    callback(id, _status(_progress), _progress)
            except subprocess.CalledProcessError as ex:
                logger.warning(f"{type(ex).__name__}: {this}: {ex}")
                callback(id, _status(-1), _progress)
                return None

    except (RuntimeError, Exception) as ex:
        logger.error(f"{type(ex).__name__}: {this}: {ex}")
        callback(id, _status(-1), _progress)
        return None
    finally:
        ds = None
        logger.debug(f"Total Perfomance Counter: {time.perf_counter() - start}")
        zclose(addressof(ifltab))

    return tmpdss
