"""DSS7 package writer

"""
import json
import os
import sys
from collections import namedtuple
from ctypes import c_char_p, c_float, c_int
from pathlib import Path

import numpy
import pyplugs
from codetiming import Timer
from cumulus_packager import heclib, logger
from cumulus_packager.configurations import PACKAGER_UPDATE_INTERVAL
from cumulus_packager.packager.handler import PACKAGE_STATUS, update_status
from osgeo import gdal, osr

gdal.UseExceptions()


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

    logger.info(
        f"Write Records to DSS using TiffDss {os.getenv('TIFFDSS_VERSION')}",
    )

    # convert the strings back to json objects; needed for pyplugs
    src = json.loads(src)
    gridcount = len(src)
    extent = json.loads(extent)
    _extent_name = extent["name"]
    _bbox = extent["bbox"]
    _progress = 0

    # assuming destination spacial references are all EPSG
    destination_srs = osr.SpatialReference()
    epsg_code = dst_srs.split(":")[-1]
    destination_srs.ImportFromEPSG(int(epsg_code))

    ###### this can go away when the payload has the resolution ######
    grid_type_name = "SHG"
    grid_type = heclib.dss_grid_type[grid_type_name]
    zcompression = heclib.compression_method["ZLIB_COMPRESSION"]
    srs_definition = heclib.spatial_reference_definition[grid_type_name]
    tz_name = "GMT"
    tz_offset = heclib.time_zone[tz_name]
    is_interval = 1

    dssfilename = Path(dst).joinpath(id).with_suffix(".dss").as_posix()

    for idx, tif in enumerate(src):
        TifCfg = namedtuple("TifCfg", tif)(**tif)
        dsspathname = f"/{grid_type_name}/{_extent_name}/{TifCfg.dss_cpart}/{TifCfg.dss_dpart}/{TifCfg.dss_epart}/{TifCfg.dss_fpart}/"

        try:
            data_type = heclib.data_type[TifCfg.dss_datatype]
            ds = gdal.Open(f"/vsis3_streaming/{TifCfg.bucket}/{TifCfg.key}")

            # GDAL Warp the Tiff to what we need for DSS
            filename_ = Path(TifCfg.key).name
            mem_raster = f"/vsimem/{filename_}"
            warp_ds = gdal.Warp(
                mem_raster,
                ds,
                format="GTiff",
                outputBounds=_bbox,
                xRes=cellsize,
                yRes=cellsize,
                targetAlignedPixels=True,
                dstSRS=destination_srs.ExportToWkt(),
                resampleAlg="bilinear",
                copyMetadata=False,
            )

            # Read data into 1D array
            raster = warp_ds.GetRasterBand(1)
            nodata = raster.GetNoDataValue()

            data = raster.ReadAsArray(resample_alg=gdal.gdalconst.GRIORA_Bilinear)
            # Flip the dataset up/down because tif and dss have different origins
            data = numpy.flipud(data)
            data_flat = data.flatten()

            # GeoTransforma and lower X Y
            xsize = warp_ds.RasterXSize
            ysize = warp_ds.RasterYSize
            adfGeoTransform = warp_ds.GetGeoTransform()
            llx = int(adfGeoTransform[0] / adfGeoTransform[1])
            lly = int(
                (adfGeoTransform[5] * ysize + adfGeoTransform[3]) / adfGeoTransform[1]
            )

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
            if nodata is not None:
                spatialGridStruct._nullValue = c_float(nodata)
            spatialGridStruct._timeZoneID = c_char_p(tz_name.encode())
            spatialGridStruct._timeZoneRawOffset = c_int(tz_offset)
            spatialGridStruct._isInterval = c_int(is_interval)
            spatialGridStruct._isTimeStamped = c_int(1)

            # Call heclib.zwrite_record() in different process space to release memory after each iteration
            t = Timer(name="accumuluated", logger=None)
            t.start()
            result = heclib.zwrite_record(
                dssfilename, spatialGridStruct, data_flat.astype(numpy.float32)
            )
            elapsed_time = t.stop()
            logger.debug(f'Processed "{TifCfg.key}" in {elapsed_time:.4f} seconds')
            if result != 0:
                logger.info(f'TiffDss write record failed for "{TifCfg.key}": {result}')

            _progress = int(((idx + 1) / gridcount) * 100)
            # Update progress at predefined interval
            if idx % PACKAGER_UPDATE_INTERVAL == 0 or idx == gridcount - 1:
                update_status(
                    id=id, status_id=PACKAGE_STATUS["INITIATED"], progress=_progress
                )
                if _progress % PACKAGER_UPDATE_INTERVAL == 0:
                    logger.info(f'Download ID "{id}" progress: {_progress}%')

        except (RuntimeError, Exception):
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback_details = {
                "filename": Path(exc_traceback.tb_frame.f_code.co_filename).name,
                "line number": exc_traceback.tb_lineno,
                "method": exc_traceback.tb_frame.f_code.co_name,
                "type": exc_type.__name__,
                "message": exc_value,
            }
            logger.error(traceback_details)

            continue

        finally:
            data = None
            raster = None
            warp_ds = None
            # Try to unlink and remove the memory raster object for each source file processed
            try:
                gdal.Unlink(mem_raster)
                mem_raster = None
            except Exception as ex:
                logger.debug("vismem unlink exception: %s", ex)

            ds = None
            spatialGridStruct = None

    # If no progress was made for any items in the payload (ex: all tifs could not be projected properly),
    # don't return a dssfilename
    if _progress == 0:
        logger.error(f'No files processed for download ID "{id}"- Progress:{_progress}')
        update_status(id=id, status_id=PACKAGE_STATUS["FAILED"], progress=_progress)
        return None

    total_time = Timer.timers["accumuluated"]
    logger.info(
        f'Total processing time for download ID "{id}" in {total_time:.4f} seconds'
    )

    return dssfilename
