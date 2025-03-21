"""Packager writer plugin

    Collect referenced GeoTiffs (COGs) into a tar gzip
"""
import json
import os
from collections import namedtuple
from tarfile import TarFile

import pyplugs
from cumulus_packager import logger
from cumulus_packager.packager.handler import PACKAGE_STATUS, update_status
from osgeo import gdal

from cumulus_packager.configurations import PACKAGER_UPDATE_INTERVAL

gdal.UseExceptions()

this = os.path.basename(__file__)

@pyplugs.register
def writer(
    id: str,
    src: str,
    extent: str,
    dst: str,
    cellsize: float,
    dst_srs: str = "EPSG:5070",
):
    """Packager writer plugin

    Parameters
    ----------
    id : str
        Download ID
    src : list
        List of objects describing the GeoTiff (COG)
    extent : dict
        Object with watershed name and bounding box
    dst : str
        Temporary directory
    cellsize : float
        Grid resolution
    dst_srs : str, optional
        Destination Spacial Reference, by default "EPSG:5070"

    Returns
    -------
    str
        FQPN to dss file
    """
    # convert the strings back to json objects; needed for pyplugs
    src = json.loads(src)
    gridcount = len(src)
    extent = json.loads(extent)
    # _extent_name = extent["name"]
    _bbox = extent["bbox"]
    _progress = 0

    # return None if no items in the 'contents'
    if len(src) < 1:
        update_status(id=id, status_id=PACKAGE_STATUS["FAILED"], progress=_progress)
        return

    tarfilename = os.path.join(dst, id) + ".tar.gz"
    try:
        tar = TarFile.open(tarfilename, "w:gz")

        for idx, tif in enumerate(src):
            TifCfg = namedtuple("TifCfg", tif)(**tif)

            filename_ = os.path.basename(TifCfg.key)

            # GDAL Warp the Tiff to what we need for DSS
            ds = gdal.Open(f"/vsis3_streaming/{TifCfg.bucket}/{TifCfg.key}")
            gdal.Warp(
                tarfile := os.path.join(dst, filename_),
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
                copyMetadata=True,
            )

            # add the tiff to the tar
            tar.add(tarfile, arcname=filename_, recursive=False)

            # callback
            _progress = int(((idx + 1) / gridcount) * 100)
            # Update progress at predefined interval
            if idx % PACKAGER_UPDATE_INTERVAL == 0 or idx == gridcount - 1:
                logger.debug(f"Progress: {_progress}")
                update_status(
                    id=id, status_id=PACKAGE_STATUS["INITIATED"], progress=_progress
                )
    except (RuntimeError, Exception) as ex:
        logger.error(f"{type(ex).__name__}: {this}: {ex}")
        update_status(id=id, status_id=PACKAGE_STATUS["FAILED"], progress=_progress)
        return None
    finally:
        ds = None
        tar.close()

    return tarfilename
