"""DSS7 package writer

"""
import json
import os
from collections import namedtuple
from ctypes import c_char_p, c_float, c_int

import numpy
import pyplugs
from cumulus_packager import heclib, logger
from cumulus_packager.packager.handler import PACKAGE_STATUS, package_status
from osgeo import gdal, osr

gdal.UseExceptions()

# gdal.SetConfigOption("CPL_DEBUG", "ON")

this = os.path.basename(__file__)

_status = lambda x: PACKAGE_STATUS[int(x)]


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
    extent = json.loads(extent)

    # return None if no items in the 'contents'
    if len(src) < 1:
        package_status(id=id, status_id=_status(-1))
        return

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

    try:
        dssfilename = os.path.join(dst, id + ".dss")

        for idx, tif in enumerate(src):
            TifCfg = namedtuple("TifCfg", tif)(**tif)
            dsspathname = f"/{grid_type_name}/{_extent_name}/{TifCfg.dss_cpart}/{TifCfg.dss_dpart}/{TifCfg.dss_epart}/{TifCfg.dss_fpart}/"
            data_type = heclib.data_type[TifCfg.dss_datatype]

            ds = gdal.Open(f"/vsis3_streaming/{TifCfg.bucket}/{TifCfg.key}")

            log_dataset(ds, "BEFORE")

            # GDAL Warp the Tiff to what we need for DSS
            filename_ = os.path.basename(TifCfg.key)
            warp_ds = gdal.Warp(
                f"/vsimem/{filename_}",
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

            log_dataset(warp_ds, "AFTER")

            # Read data into 1D array
            raster = warp_ds.GetRasterBand(1)
            nodata = raster.GetNoDataValue()
            data = raster.ReadAsArray(resample_alg=gdal.gdalconst.GRIORA_Bilinear)
            if "PRECIP" in TifCfg.dss_cpart.upper() and nodata != 0:
                data[data == nodata] = 0
                nodata = 0
            data_flat = data.flatten()

            # GeoTransforma and lower X Y
            xsize, ysize = warp_ds.RasterXSize, warp_ds.RasterYSize
            adfGeoTransform = warp_ds.GetGeoTransform()
            llx = int(adfGeoTransform[0] / adfGeoTransform[1])
            lly = int(
                (adfGeoTransform[5] * ysize + adfGeoTransform[3]) / adfGeoTransform[1]
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
                if nodata is not None:
                    spatialGridStruct._nullValue = c_float(nodata)
                spatialGridStruct._timeZoneID = c_char_p(tz_name.encode())
                spatialGridStruct._timeZoneRawOffset = c_int(tz_offset)
                spatialGridStruct._isInterval = c_int(is_interval)
                spatialGridStruct._isTimeStamped = c_int(1)

                _ = heclib.zwrite_record(
                    dssfilename=dssfilename,
                    gridStructStore=spatialGridStruct,
                    data_flat=data_flat.astype(numpy.float32),
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
        warp_ds = None

    return dssfilename
