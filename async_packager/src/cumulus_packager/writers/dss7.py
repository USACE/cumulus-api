"""DSS7 package writer

"""
import json
import multiprocessing
import os
from collections import namedtuple
from ctypes import c_char_p, c_float, c_int

import numpy
import pyplugs
from cumulus_packager import heclib, logger
from cumulus_packager.configurations import LOGGER_LEVEL, PACKAGER_UPDATE_INTERVAL
from cumulus_packager.packager.handler import PACKAGE_STATUS, update_status
from osgeo import gdal, osr

gdal.UseExceptions()

# gdal.SetConfigOption("CPL_DEBUG", "ON")

this = os.path.basename(__file__)


def log_dataset(gdal_dataset, *args):
    logger.debug(f"{args}")

    logger.debug(f"{gdal_dataset.RasterXSize=}")
    logger.debug(f"{gdal_dataset.RasterYSize=}")
    logger.debug(f"{gdal_dataset.RasterCount=}")
    gdal_spatial_ref = gdal_dataset.GetSpatialRef()
    logger.debug(f"{gdal_spatial_ref.ExportToPrettyWkt()=}")

    raster = gdal_dataset.GetRasterBand(1)
    logger.debug(f"{raster.GetNoDataValue()=}")

    data = raster.ReadAsArray(resample_alg=gdal.gdalconst.GRIORA_Bilinear)
    logger.debug(f"{data.min()=}; {data.max()=}; {data.mean()=}; {data.size=}")

    gdal_spatial_ref = None
    data = None
    raster = None

    return


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

    for idx, tif in enumerate(src):
        TifCfg = namedtuple("TifCfg", tif)(**tif)
        dsspathname = f"/{grid_type_name}/{_extent_name}/{TifCfg.dss_cpart}/{TifCfg.dss_dpart}/{TifCfg.dss_epart}/{TifCfg.dss_fpart}/"

        try:
            dssfilename = os.path.join(dst, id + ".dss")
            data_type = heclib.data_type[TifCfg.dss_datatype]
            ds = gdal.Open(f"/vsis3_streaming/{TifCfg.bucket}/{TifCfg.key}")

            if LOGGER_LEVEL.lower == "debug":
                log_dataset(ds, "BEFORE")

            # GDAL Warp the Tiff to what we need for DSS
            filename_ = os.path.basename(TifCfg.key)
            warp_ds = gdal.Warp(
                mem_raster := f"/vsimem/{filename_}",
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

            if LOGGER_LEVEL.lower == "debug":
                log_dataset(warp_ds, "AFTER")

            # Read data into 1D array
            raster = warp_ds.GetRasterBand(1)
            _nodata = raster.GetNoDataValue()
            nodata = 9999 if _nodata is None else _nodata

            data = numpy.flipud(
                raster.ReadAsArray(resample_alg=gdal.gdalconst.GRIORA_Bilinear)
            ).flatten()

            # GeoTransforma and lower X Y
            xsize, ysize = warp_ds.RasterXSize, warp_ds.RasterYSize
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
            spatialGridStruct._nullValue = c_float(nodata)
            spatialGridStruct._timeZoneID = c_char_p(tz_name.encode())
            spatialGridStruct._timeZoneRawOffset = c_int(tz_offset)
            spatialGridStruct._isInterval = c_int(is_interval)
            spatialGridStruct._isTimeStamped = c_int(1)

            # Call heclib.zwrite_record() in different process space to release memory after each iteration
            _p = multiprocessing.Process(
                target=heclib.zwrite_record,
                args=(dssfilename, spatialGridStruct, data.astype(numpy.float32)),
            )
            _p.start()
            _p.join()

            _progress = int(((idx + 1) / gridcount) * 100)
            # Update progress at predefined interval
            if idx % PACKAGER_UPDATE_INTERVAL == 0 or idx == gridcount - 1:
                logger.debug(f"Progress: {_progress}")
                update_status(
                    id=id, status_id=PACKAGE_STATUS["INITIATED"], progress=_progress
                )

            # try to unlink the memory file and continue if it causes a problem
            try:
                gdal.Unlink(mem_raster)
            except RuntimeError as ex:
                logger.error(f"{type(ex).__name__}: {this}: {ex}")
                continue

        except (RuntimeError, Exception) as ex:
            logger.error(f"{type(ex).__name__}: {this}: {ex}")
            update_status(id=id, status_id=PACKAGE_STATUS["FAILED"], progress=_progress)
            return None

        finally:
            spatialGridStruct = None
            adfGeoTransform = None
            raster = None
            nodata = None
            data = None
            warp_ds = None
            TifCfg = None
            data_type = None
            ds = None

    grid_type = None
    zcompression = None
    srs_definition = None
    tz_offset = None
    src = None

    return dssfilename
