"""Testing with ctypes
"""
import ctypes
from ctypes import (
    CDLL,
    POINTER,
    LibraryLoader,
    Structure,
    addressof,
    c_char,
    c_char_p,
    c_double,
    c_float,
    c_int,
    c_longlong,
    c_long,
    c_uint32,
    c_void_p,
    memset,
    pointer,
    sizeof,
)

from osgeo import gdal
import numpy as np


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
        ("_data", (c_void_p)),
    ]


tiffdss = LibraryLoader(CDLL).LoadLibrary("libtiffdss.so")

zopen = tiffdss.opendss
zopen.argtypes = [c_longlong, c_char_p]
zopen.restype = c_int

zclose = tiffdss.closedss
zclose.argtypes = [c_longlong]
zclose.restype = c_int

write_to_dss = tiffdss.writeToDss
write_to_dss.argtypes = [
    c_longlong,
    c_char_p,
    c_char_p,
    c_char_p,
    c_char_p,
    zStructSpatialGrid,
]
write_to_dss.restype = c_int


ds = gdal.Open("/dss-test-data/tiff/MRMS_MultiSensor.tif")
# ds = gdal.Open(
#     "/dss-test-data/tiff/MRMS_MultiSensor_QPE_01H_Pass1_00.00_20220216-170000.tif"
# )
x_size = ds.RasterXSize
y_size = ds.RasterYSize

# c_float_p = ctypes.POINTER(ctypes.c_float)

data = ds.GetRasterBand(1).ReadAsArray()
data = data.astype(np.float64)
data = data.flatten()
# data_p = data.ctypes.data_as(c_float_p)
data_p = data.ctypes.data_as(POINTER(c_float))

ifltab = c_longlong(250)
memset(addressof(ifltab), 0, 250 * sizeof(c_long))
ret = zopen(addressof(ifltab), c_char_p(b"/app/async_packager/tiffdss/src/newfile.dss"))

gridStructStore = zStructSpatialGrid()
gridStructStore.pathname = ctypes.c_char_p(
    b"/SHG/WS/PRECIP/16FEB2022:1700/16FEB2022:1800/MRMS QPE/"
)
gridStructStore._dataSource = ctypes.c_char_p(b"INTERNAL")
gridStructStore._version = 1
gridStructStore._dataUnits = c_char_p(b"mm")
gridStructStore._numberOfCellsX = x_size
gridStructStore._numberOfCellsY = y_size
gridStructStore._lowerLeftCellX = 0
gridStructStore._lowerLeftCellY = 0
gridStructStore._cellSize = c_float(2000)
gridStructStore._compressionMethod = 26

gridStructStore_numberOfRanges = 5

gridStructStore._srsDefinitionType = 1
gridStructStore._srsName = c_char_p(b"")
gridStructStore._srsDefinition = c_char_p(b"")
gridStructStore._xCoordOfGridCellZero = c_float(0)
gridStructStore._yCoordOfGridCellZero = c_float(0)
gridStructStore._nullValue = c_float(-9999)
gridStructStore._isInterval = 1
gridStructStore._isTimeStamped = 1
# gridStructStore._data = data_p

grid_type = b"shg-time"
data_type = b"per-cum"
tz = b"gmt"
compression = b"zlib"

try:
    ret = write_to_dss(
        addressof(ifltab),
        c_char_p(grid_type),
        c_char_p(data_type),
        data_p,
        c_char_p(tz),
        c_char_p(compression),
        gridStructStore,
    )
    print(f"Return: {ret}")
except Exception as ex:
    print(ex)
finally:
    res = zclose(addressof(ifltab))

print("Done")

ds = None
