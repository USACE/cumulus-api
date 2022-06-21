"""Packager writer plugin

    COG --> DSS7
"""
import json
import os
from collections import namedtuple
from ctypes import c_char_p, c_float, c_int

import numpy
import pyplugs
from cumulus_packager import heclib, logger

from cumulus_packager.packager.handler import PACKAGE_STATUS, package_status
from osgeo import gdal

gdal.UseExceptions()

this = os.path.basename(__file__)

_status = lambda x: PACKAGE_STATUS[int(x)]


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
    callback : str, optional
        callback function sending message to the DB, by default None, by default None
        implemented as pyplugs plugin

    Returns
    -------
    str
        FQPN to dss file
    """
    # convert the strings back to json objects; needed for pyplugs
    src = json.loads(src)
    extent = json.loads(extent)

    # return None if no items in the 'contents'
    if len(src) < 1:
        package_status(id=id, status_id=_status(-1))
        return

    _extent_name = extent["name"]
    _bbox = extent["bbox"]
    _progress = 0
    _nodata = 9999

    ###### this can go away when the payload has the resolution ######
    cellsize = 2000 if cellsize is None else None
    grid_type_name = "SHG"
    grid_type = heclib.dss_grid_type[grid_type_name]
    zcompression = heclib.compression_method["ZLIB_COMPRESSION"]
    srs_definition = heclib.spatial_reference_definition[grid_type_name]
    tz_name = "GMT"
    tz_offset = heclib.time_zone[tz_name]
    is_interval = 1

    try:
        dssfilename = os.path.join(dst, id + ".dss")

        for idx, tif in enumerate(src):
            TifCfg = namedtuple("TifCfg", tif)(**tif)

            data_type = heclib.data_type[TifCfg.dss_datatype]

            filename_ = os.path.basename(TifCfg.key)
            dsspathname = f"/{grid_type_name}/{_extent_name}/{TifCfg.dss_cpart}/{TifCfg.dss_dpart}/{TifCfg.dss_epart}/{TifCfg.dss_fpart}/"

            if len(TifCfg.dss_epart) < 14:
                is_interval = 0

            ds = gdal.Open(f"/vsis3_streaming/{TifCfg.bucket}/{TifCfg.key}")

            # GDAL Warp the Tiff to what we need for DSS
            gdal.Warp(
                tmptiff := f"/vsimem/{filename_}",
                ds,
                format="GTiff",
                outputBounds=_bbox,
                xRes=cellsize,
                yRes=cellsize,
                targetAlignedPixels=True,
                dstSRS=dst_srs,
                outputType=gdal.GDT_Float32,
                resampleAlg="bilinear",
                dstNodata=_nodata,
                copyMetadata=False,
            )
            logger.debug(f"{tmptiff=}")

            ds = gdal.Open(tmptiff)
            xsize, ysize = ds.RasterXSize, ds.RasterYSize
            adfGeoTransform = ds.GetGeoTransform()
            llx = int(adfGeoTransform[0] / adfGeoTransform[1])
            lly = int(
                (adfGeoTransform[5] * ysize + adfGeoTransform[3]) / adfGeoTransform[1]
            )

            logger.debug(f"{xsize=}, {ysize=}, {llx=}, {lly=}")

            # get stats from the array
            _data = numpy.float32(ds.GetRasterBand(1).ReadAsArray())
            data = _data.flatten()
            logger.debug(f"{data=}")

            gridStats = heclib.GridStats()
            gridStats.minimum = c_float(numpy.nanmin(data))
            gridStats.maximum = c_float(numpy.nanmax(data))
            gridStats.meanval = c_float(numpy.nanmean(data))
            logger.debug(
                f"GridStats: {gridStats.minimum=} {gridStats.maximum=} {gridStats.meanval=}"
            )

            try:
                spatialGridStruct = heclib.zStructSpatialGrid()
                spatialGridStruct.pathname = c_char_p(dsspathname.encode())
                spatialGridStruct._structVersion = c_int(-100)
                spatialGridStruct._type = c_int(grid_type)
                spatialGridStruct._version = c_int(1)
                spatialGridStruct._dataUnits = c_char_p(str.encode(TifCfg.dss_unit))
                spatialGridStruct._dataType = c_int(data_type)
                spatialGridStruct._dataSource = c_char_p("INTERNAL".encode())
                spatialGridStruct._lowerLeftCellX = c_int(llx)
                spatialGridStruct._lowerLeftCellY = c_int(lly)
                spatialGridStruct._numberOfCellsX = c_int(xsize)
                spatialGridStruct._numberOfCellsY = c_int(ysize)
                spatialGridStruct._cellSize = c_float(cellsize)
                spatialGridStruct._compressionMethod = c_int(zcompression)
                spatialGridStruct._srsName = c_char_p(grid_type_name.encode())
                spatialGridStruct._srsDefinitionType = c_int(1)
                spatialGridStruct._srsDefinition = c_char_p(srs_definition.encode())
                spatialGridStruct._xCoordOfGridCellZero = c_float(0)
                spatialGridStruct._yCoordOfGridCellZero = c_float(0)
                spatialGridStruct._nullValue = c_float(_nodata)
                spatialGridStruct._timeZoneID = c_char_p(tz_name.encode())
                spatialGridStruct._timeZoneRawOffset = c_int(tz_offset)
                spatialGridStruct._isInterval = c_int(is_interval)
                spatialGridStruct._isTimeStamped = c_int(1)

                _ = heclib.zwrite_record(
                    dssfilename=dssfilename,
                    gridStructStore=spatialGridStruct,
                    data_flat=data,
                    gridStats=gridStats,
                )

                # callback
                _progress = idx / len(src)
                logger.debug(f"Progress: {_progress}")

                package_status(
                    id=id,
                    status_id=_status(_progress),
                    progress=_progress,
                )
            except Exception as ex:
                logger.warning(f"{type(ex).__name__}: {this}: {ex}")
                package_status(id=id, status_id=_status(-1), progress=_progress)
                return None

    except (RuntimeError, Exception) as ex:
        logger.error(f"{type(ex).__name__}: {this}: {ex}")
        package_status(id=id, status_id=_status(-1), progress=_progress)
        return None
    finally:
        ds = None

    return dssfilename
