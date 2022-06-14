"""Packager writer plugin

    COG --> DSS7
"""

from ctypes import (
    CDLL,
    POINTER,
    LibraryLoader,
    Structure,
    addressof,
    c_char_p,
    c_float,
    c_int,
    c_longlong,
    c_size_t,
    c_void_p,
    cast,
    memset,
    pointer,
    sizeof,
)


import numpy as np
from osgeo import gdal

from cumulus_packager import heclib


class GridStats(Structure):
    _fields_ = [
        ("minimum", c_float),
        ("maximum", c_float),
        ("meanval", c_float),
    ]


class zStructSpatialGrid(Structure):
    _fields_ = [
        ("structType", c_int),
        ("pathname", c_char_p),
        ("_structVersion", c_int),
        ("_type", c_int),
        ("_version", c_int),
        ("_dataUnits", c_char_p),
        ("_dataType", c_int),
        ("_dataSource", c_char_p),
        ("_lowerLeftCellX", c_int),
        ("_lowerLeftCellY", c_int),
        ("_numberOfCellsX", c_int),
        ("_numberOfCellsY", c_int),
        ("_cellSize", c_float),
        ("_compressionMethod", c_int),
        ("_sizeofCompressedElements", c_int),
        ("_compressionParameters", c_void_p),
        ("_srsName", c_char_p),
        ("_srsDefinitionType", c_int),
        ("_srsDefinition", c_char_p),
        ("_xCoordOfGridCellZero", c_float),
        ("_yCoordOfGridCellZero", c_float),
        ("_nullValue", c_float),
        ("_timeZoneID", c_char_p),
        ("_timeZoneRawOffset", c_int),
        ("_isInterval", c_int),
        ("_isTimeStamped", c_int),
        ("_numberOfRanges", c_int),
        ("_storageDataType", c_int),
        ("_maxDataValue", c_void_p),
        ("_minDataValue", c_void_p),
        ("_meanDataValue", c_void_p),
        ("_rangeLimitTable", c_void_p),
        ("_numberEqualOrExceedingRangeLimit", c_int),
        ("_data", c_void_p),
    ]


tiffdss = LibraryLoader(CDLL).LoadLibrary("libtiffdss.so")

# define the data array as a pointer for the C function
ND_POINTER_1 = np.ctypeslib.ndpointer(dtype=np.float32, ndim=1, flags="C")
write_record = tiffdss.writeRecord

# define the C function arguments
# c_longlong,
# POINTER(zStructSpatialGrid),
# ND_POINTER_1,
# c_size_t,
write_record.argtypes = [
    c_longlong,
    POINTER(zStructSpatialGrid),
    ND_POINTER_1,
    c_size_t,
    POINTER(GridStats),
]
write_record.restype = c_int

zopen = tiffdss.opendss
zopen.argtypes = [c_longlong, c_char_p]
zopen.restype = c_int

zclose = tiffdss.closedss
zclose.argtypes = [c_longlong]
zclose.restype = c_int


ds = gdal.Open("/dss-test-data/tiff/MRMS_MultiSensor.tif")
raster = ds.GetRasterBand(1)
geo_transorm = ds.GetGeoTransform()
x_size = raster.XSize
y_size = raster.YSize
d_size = c_size_t(x_size * y_size)

_min, _max, _mean, _stdv = raster.GetStatistics(1, 1)
grid_stats = GridStats(minimum=_min, maximum=_max, meanval=_mean)

nodata = -9999 if raster.GetNoDataValue() is None else raster.GetNoDataValue()
# _min_p = pointer(c_float(_min))
# _min_p_void = cast(_min_p, POINTER(c_void_p))

print(f"{x_size=}", f"{y_size=}", f"{d_size=}", end="\n")
print(f"{_min=}", f"{_max=}", f"{_mean=}", f"{_stdv=}", f"{nodata=}", end="\n")

# get the data as numpy array, flatten to 1D and cast to c_void_p (void *)
raster_array = np.float32(raster.ReadAsArray())
data_ = raster_array.flatten()
# data = data_.ctypes.data_as(POINTER(c_float))

# this is a fake array for testing
# rng = np.random.default_rng(12345)
# data_array = rng.random((200, 300), dtype=np.float32)
# data_flatten = data_array.flatten()
# _data = data_flatten.ctypes.data_as(c_void_p)

# define the dss file table to pass for open, write and close
ifltab = c_longlong(250)
memset(addressof(ifltab), 0, 250 * sizeof(c_longlong))

# Create a struct for the spatial grid and populate
spatialGridStruct = zStructSpatialGrid()
spatialGridStruct.pathname = (
    "/SHG/WS/PRECIP/16FEB2022:1600/16FEB2022:1700/MRMS QPE/".encode()
)
spatialGridStruct._structVersion = -100
spatialGridStruct._type = heclib.ALBERS
spatialGridStruct._version = 1
spatialGridStruct._dataUnits = c_char_p("MM".encode())
spatialGridStruct._dataType = 1
spatialGridStruct._dataSource = c_char_p("INTERNAL".encode())
spatialGridStruct._lowerLeftCellX = 0
spatialGridStruct._lowerLeftCellY = 0
spatialGridStruct._numberOfCellsX = c_int(x_size)
spatialGridStruct._numberOfCellsY = c_int(y_size)
spatialGridStruct._cellSize = c_float(2000)
spatialGridStruct._compressionMethod = 26
spatialGridStruct._srsName = c_char_p("ALBERS".encode())
spatialGridStruct._srsDefinitionType = 1
spatialGridStruct._srsDefinition = c_char_p(heclib.SHG_SRC_DEFINITION)
spatialGridStruct._xCoordOfGridCellZero = c_float(0)
spatialGridStruct._yCoordOfGridCellZero = c_float(0)
spatialGridStruct._nullValue = c_float(nodata)
spatialGridStruct._timeZoneID = c_char_p("GMT".encode())
spatialGridStruct._timeZoneRawOffset = c_int(0)
spatialGridStruct._isInterval = c_int(1)
spatialGridStruct._isTimeStamped = c_int(1)

# compute C internal?
# spatialGridStruct._minDataValue = cast(pointer(c_float(_min)), c_void_p)
# spatialGridStruct._maxDataValue = cast(pointer(c_float(_max)), c_void_p)
# spatialGridStruct._meanDataValue = cast(pointer(c_float(_mean)), c_void_p)

# spatialGridStruct._data = data


# the C function takes a pointer for the struct
gridStructStore_pointer = pointer(spatialGridStruct)
gridStats_pointer = pointer(grid_stats)


# OPEN DSS
tmpdss = b"/app/async_packager/tiffdss/nbm.dss"

ret = zopen(addressof(ifltab), c_char_p(tmpdss))
print(f"Open: {ret}")


# WRITE DSS
ret = write_record(
    addressof(ifltab),
    gridStructStore_pointer,
    data_,
    data_.size,
    gridStats_pointer,
)
# ret = write_record(addressof(ifltab), gridStructStore_pointer)
# ret = write_record(addressof(ifltab))
print(f"Write: {ret}")

# CLOSE DSS
ret = zclose(addressof(ifltab))
print(f"Close: {ret}")


ds = None
