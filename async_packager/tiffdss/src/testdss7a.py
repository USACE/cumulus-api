"""Testing data array
"""

import ctypes
from curses import can_change_color

import numpy as np
from cumulus_packager.heclib import GridStats
from cumulus_packager import heclib

from cumulus_packager.heclib import zStructSpatialGrid

tiffdss = ctypes.LibraryLoader(ctypes.CDLL).LoadLibrary("libtiffdss.so")

ND_POINTER_1 = np.ctypeslib.ndpointer(dtype=np.float32, ndim=1, flags="C")


def main():
    dssfilename = "/app/async_packager/tiffdss/src/newfile.dss"

    # create array X = [1 1 1 1 1]
    X = np.ones((100, 100), dtype=np.float32)
    xsize, ysize = X.shape
    X_flat = X.flatten()

    gridStats = GridStats()
    gridStats.minimum = ctypes.c_float(X.min())
    gridStats.maximum = ctypes.c_float(X.max())
    gridStats.meanvalue = ctypes.c_float(X.mean())

    spatialGridStruct = zStructSpatialGrid()
    spatialGridStruct.pathname = ctypes.c_char_p(
        ("/SHG/WS/PRECIP/16FEB2022:1600/16FEB2022:1700/MRMS QPE/".encode())
    )
    spatialGridStruct._structVersion = -100
    spatialGridStruct._type = heclib.DssGridType.SPECIFIED_GRID_TYPE.value
    spatialGridStruct._version = 1
    spatialGridStruct._dataUnits = ctypes.c_char_p("MM".encode())
    spatialGridStruct._dataType = 1
    spatialGridStruct._dataSource = ctypes.c_char_p("INTERNAL".encode())
    spatialGridStruct._lowerLeftCellX = 0
    spatialGridStruct._lowerLeftCellY = 0
    spatialGridStruct._numberOfCellsX = ctypes.c_int(xsize)
    spatialGridStruct._numberOfCellsY = ctypes.c_int(ysize)
    spatialGridStruct._cellSize = ctypes.c_float(2000)
    spatialGridStruct._compressionMethod = 26
    spatialGridStruct._srsName = ctypes.c_char_p("UTM16".encode())
    spatialGridStruct._srsDefinitionType = 1
    spatialGridStruct._srsDefinition = ctypes.c_char_p(
        (
            heclib.UTM_SRC_DEFINITION % ("1", "6", str(-183 + 16 * 6), "10000000")
        ).encode()
    )
    spatialGridStruct._xCoordOfGridCellZero = ctypes.c_float(0)
    spatialGridStruct._yCoordOfGridCellZero = ctypes.c_float(0)
    spatialGridStruct._nullValue = ctypes.c_float(-9999)
    spatialGridStruct._timeZoneID = ctypes.c_char_p("GMT".encode())
    spatialGridStruct._timeZoneRawOffset = ctypes.c_int(0)
    spatialGridStruct._isInterval = ctypes.c_int(1)
    spatialGridStruct._isTimeStamped = ctypes.c_int(1)

    spatialGridStruct_pointer = ctypes.pointer(spatialGridStruct)
    gridStats_pointer = ctypes.pointer(gridStats)
    dssfilename_pointer = ctypes.c_char_p(dssfilename.encode())

    tiffdss.writeRecord.argtypes = (
        ctypes.c_char_p,
        ctypes.POINTER(zStructSpatialGrid),
        ND_POINTER_1,
        ctypes.POINTER(GridStats),
    )
    tiffdss.writeRecord.restype = ctypes.c_int

    res = tiffdss.writeRecord(
        dssfilename_pointer,
        spatialGridStruct_pointer,
        X_flat,
        gridStats_pointer,
    )

    print(f"Result: {res}")


if __name__ == "__main__":
    main()
