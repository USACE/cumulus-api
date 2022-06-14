"""_summary_
"""

import ctypes


class zStructSpatialGrid(ctypes.Structure):
    _fields_ = [
        ("structType", ctypes.c_int),
        ("pathname", ctypes.c_char_p),
        ("_structVersion", ctypes.c_int),
        ("_type", ctypes.c_int),
        ("_version", ctypes.c_int),
        ("_dataUnits", ctypes.c_char_p),
        ("_dataType", ctypes.c_int),
        ("_dataSource", ctypes.c_char_p),
        ("_lowerLeftCellX", ctypes.c_int),
        ("_lowerLeftCellY", ctypes.c_int),
        ("_numberOfCellsX", ctypes.c_int),
        ("_numberOfCellsY", ctypes.c_int),
        ("_cellSize", ctypes.c_float),
        ("_compressionMethod", ctypes.c_int),
        ("_sizeofCompressedElements", ctypes.c_int),
        ("_compressionParameters", ctypes.c_void_p),
        ("_srsName", ctypes.c_char_p),
        ("_srsDefinitionType", ctypes.c_int),
        ("_srsDefinition", ctypes.c_char_p),
        ("_xCoordOfGridCellZero", ctypes.c_float),
        ("_yCoordOfGridCellZero", ctypes.c_float),
        ("_nullValue", ctypes.c_float),
        ("_timeZoneID", ctypes.c_char_p),
        ("_timeZoneRawOffset", ctypes.c_int),
        ("_isInterval", ctypes.c_int),
        ("_isTimeStamped", ctypes.c_int),
        ("_numberOfRanges", ctypes.c_int),
        ("_storageDataType", ctypes.c_int),
        ("_maxDataValue", ctypes.c_void_p),
        ("_minDataValue", ctypes.c_void_p),
        ("_meanDataValue", ctypes.c_void_p),
        ("_rangeLimitTable", ctypes.c_void_p),
        ("_numberEqualOrExceedingRangeLimit", ctypes.c_int),
        ("_data", (ctypes.c_void_p)),
    ]


tiffdss = ctypes.LibraryLoader(ctypes.CDLL).LoadLibrary("libtiffdss.so")

tiffdss.print_GridStruct.argtypes = [ctypes.POINTER(zStructSpatialGrid)]
tiffdss.print_GridStruct.restype = ctypes.c_int


gridStructStore = zStructSpatialGrid()
gridStructStore.pathname = ctypes.c_char_p(
    "/SHG/WS/PRECIP/16FEB2022:1600/16FEB2022:1700/MRMS QPE/".encode()
)
# gridStructStore._dataSource = ctypes.c_char_p(b"INTERNAL")
# gridStructStore._version = 1
# gridStructStore._dataUnits = ctypes.c_char_p(b"mm")
# gridStructStore._numberOfCellsX = 100
# gridStructStore._numberOfCellsY = 100
# gridStructStore._lowerLeftCellX = 0
# gridStructStore._lowerLeftCellY = 0
# gridStructStore._cellSize = ctypes.c_float(2000)
# gridStructStore._compressionMethod = 26

# gridStructStore_numberOfRanges = 5

# gridStructStore._srsDefinitionType = 1
# gridStructStore._srsName = ctypes.c_char_p(b"")
# gridStructStore._srsDefinition = ctypes.c_char_p(b"")
# gridStructStore._xCoordOfGridCellZero = ctypes.c_float(0)
# gridStructStore._yCoordOfGridCellZero = ctypes.c_float(0)
# gridStructStore._nullValue = ctypes.c_float(-9999)
# gridStructStore._isInterval = 1
# gridStructStore._isTimeStamped = 1

_min = ctypes.c_float(12.12)
gridStructStore._minDataValue = ctypes.addressof(_min)
# gridStructStore._minDataValue = ctypes.cast(
#     ctypes.pointer((ctypes.c_float(12.12))), ctypes.c_void_p
# )
# # gridStructStore._data = data_p

gridStructStore_pointer = ctypes.pointer(gridStructStore)
tiffdss.print_GridStruct(gridStructStore_pointer)
