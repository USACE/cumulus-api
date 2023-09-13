"""Module 'heclib'

Enumerations, constants and functions

"""

from ctypes import (
    CDLL,
    POINTER,
    LibraryLoader,
    Structure,
    c_char_p,
    c_float,
    c_int,
    c_void_p,
    pointer,
)
from enum import Enum, auto

import numpy

# libtiffdss.so is compiled and put in /usr/lib during image creation
tiffdss = LibraryLoader(CDLL).LoadLibrary("libtiffdss.so")
"""ctypes.CDLL: tiff to dss shared object"""

FLOAT_MAX = 3.40282347e38
UNDEFINED = -FLOAT_MAX

HRAP_SRC_DEFINITION = 'PROJCS["Stereographic_CONUS_HRAP",\
GEOGCS["GCS_Sphere_LFM",DATUM["D_Sphere_LFM",\
SPHEROID["Shpere_LFM",6371200.0,0.0]],PRIMEM["Greenwich",0.0],\
UNIT["Degree",0.0174532925199433]],\
PROJECTION["Stereographic_North_Pole"],\
PARAMETER["False_Easting",1909762.5],PARAMETER["False_Northing",7624762.5],\
PARAMETER["Central_Meridian",-105.0],PARAMETER["Standard_Parallel_1",60.0],\
UNIT["Meter",1.0]]'
"""str: HRAP WKT"""

SHG_SRC_DEFINITION = 'PROJCS["USA_Contiguous_Albers_Equal_Area_Conic_USGS_version",\
GEOGCS["GCS_North_American_1983",DATUM["D_North_American_1983",\
SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],\
UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],\
PARAMETER["False_Easting",0.0],PARAMETER["False_Northing",0.0],\
PARAMETER["Central_Meridian",-96.0],PARAMETER["Standard_Parallel_1",29.5],\
PARAMETER["Standard_Parallel_2",45.5],PARAMETER["Latitude_Of_Origin",23.0],\
UNIT["Meter",1.0]]'
"""str: SHG WKT"""

# Parameters: utmZone, utmHemisphere, central_meridian, false_northing
# if (_utmHemisphere.equals("S")) falseNorthing = 10000000;
#  centralMeridian = -183 + _utmZone * 6;
UTM_SRC_DEFINITION = 'PROJCS["UTM_ZONE_%s%s_WGS84",\
GEOGCS["WGS_84",DATUM["WGS_1984",SPHEROID["WGS84",6378137,298.257223563]],\
PRIMEM["Greenwich",0],UNIT["degree",0.01745329251994328]],\
UNIT["Meter",1.0],PROJECTION["Transverse_Mercator"],\
PARAMETER["latitude_of_origin",0],\
PARAMETER["central_meridian",%s],\
PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],\
PARAMETER["false_northing",%s],\
AXIS["Easting",EAST],AXIS["Northing",NORTH]]'
"""str: UTM WKT"""

# ProjectionDatum
class ProjectionDatum(Enum):
    UNDEFINED_PROJECTION_DATUM = 0
    NAD_27 = auto()
    NAD_83 = auto()


projection_datum = {i.name: i.value for i in ProjectionDatum}


# CompressionMethod
class CompressionMethod(Enum):
    UNDEFINED_COMPRESSION_METHOD = 0
    NO_COMPRESSION = auto()
    ZLIB_COMPRESSION = 26


compression_method = {i.name: i.value for i in CompressionMethod}

# StorageDataType
class StorageDataType(Enum):
    GRID_FLOAT = 0
    GRID_INT = auto()
    GRID_DOUBLE = auto()
    GRID_LONG = auto()


storage_data_type = {i.name: i.value for i in StorageDataType}

# DataType
class DataType(Enum):
    PER_AVER = 0
    PER_CUM = auto()
    INST_VAL = auto()
    INST_CUM = auto()
    FREQ = auto()
    INVALID = auto()


data_type = {i.name.replace("_", "-"): i.value for i in DataType}

# GridStructVersion
class GridStructVersion(Enum):
    VERSION_100 = -100


grid_struct_version = {i.name: i.value for i in GridStructVersion}

# DssGridType
class DssGridType(Enum):
    UNDEFINED_GRID_TYPE = 400
    HRAP = 410
    SHG = ALBERS = 420
    SPECIFIED_GRID_TYPE = 430


dss_grid_type = {i.name: i.value for i in DssGridType}

# DssGridTypeName
class DssGridTypeName(Enum):
    HRAP = "HRAP"
    SHG = "ALBERS"
    UTM = "UMT%s%s"


dss_grid_type_name = {i.name: i.value for i in DssGridTypeName}

# SpatialRefereceDefinition
class SpatialReferenceDefinition(Enum):
    UNDEFINED_GRID_TYPE = None
    HRAP = HRAP_SRC_DEFINITION
    SHG = ALBERS = SHG_SRC_DEFINITION
    SPECIFIED_GRID_TYPE = None


spatial_reference_definition = {i.name: i.value for i in SpatialReferenceDefinition}

# TimeZones
class TimeZone(Enum):
    GMT = UTC = 0
    AST = 4
    EST = auto()
    CST = auto()
    MST = auto()
    PST = auto()
    AKST = auto()
    HST = auto()


time_zone = {i.name: i.value for i in TimeZone}


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

    def __init__(self, *args, **kw):
        self._nullValue = UNDEFINED
        super().__init__(*args, **kw)

def zwrite_record(
    dssfilename: str,
    gridStructStore: zStructSpatialGrid,
    data_flat: numpy,
):
    """Write the data array to DSS record using the 'writeRecord' C function

    Parameters
    ----------
    dssfilename : str
        DSS file name and path
    gridStructStore : zStructSpatialGrid
        ctypes structure
    data_flat : numpy
        1D numpy array
    gridStats : GridStats
        ctypes structure

    Returns
    -------
    int
        Response from the C function
    """
    ND_POINTER_1 = numpy.ctypeslib.ndpointer(dtype=numpy.float32, ndim=1, flags="C")

    tiffdss.writeRecord_External.argtypes = (
        c_char_p,
        POINTER(zStructSpatialGrid),
        ND_POINTER_1,
    )
    tiffdss.writeRecord_External.restype = c_int

    res = tiffdss.writeRecord_External(
        c_char_p(dssfilename.encode()),
        pointer(gridStructStore),
        data_flat,
    )

    return res
