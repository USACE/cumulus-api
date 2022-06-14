"""enumerations for heclib
"""

from enum import Enum
from ctypes import (
    Structure,
    c_char_p,
    c_float,
    c_int,
    c_void_p,
)


HRAP_SRC_DEFINITION = 'PROJCS["Stereographic_CONUS_HRAP",\
GEOGCS["GCS_Sphere_LFM",DATUM["D_Sphere_LFM",\
SPHEROID["Shpere_LFM",6371200.0,0.0]],PRIMEM["Greenwich",0.0],\
UNIT["Degree",0.0174532925199433]],\
PROJECTION["Stereographic_North_Pole"],\
PARAMETER["False_Easting",1909762.5],PARAMETER["False_Northing",7624762.5],\
PARAMETER["Central_Meridian",-105.0],PARAMETER["Standard_Parallel_1",60.0],\
UNIT["Meter",1.0]]'

SHG_SRC_DEFINITION = 'PROJCS["USA_Contiguous_Albers_Equal_Area_Conic_USGS_version",\
GEOGCS["GCS_North_American_1983",DATUM["D_North_American_1983",\
SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],\
UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],\
PARAMETER["False_Easting",0.0],PARAMETER["False_Northing",0.0],\
PARAMETER["Central_Meridian",-96.0],PARAMETER["Standard_Parallel_1",29.5],\
PARAMETER["Standard_Parallel_2",45.5],PARAMETER["Latitude_Of_Origin",23.0],\
UNIT["Meter",1.0]]'

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

# ProjectionDatum
class ProjectionDatum(Enum):
    UNDEFINED_PROJECTION_DATUM, NAD_27, NAD_83 = 0, 1, 2


UNDEFINED_PROJECTION_DATUM, NAD_27, NAD_83 = 0, 1, 2

# CompressionMethod
class CompressionMethod(Enum):
    UNDEFINED_COMPRESSION_METHOD, NO_COMPRESSION, ZLIB_COMPRESSION = 0, 1, 26


UNDEFINED_COMPRESSION_METHOD, NO_COMPRESSION, ZLIB_COMPRESSION = 0, 1, 26


# StorageDataType
class StorageDataType(Enum):
    GRID_FLOAT, GRID_INT, GRID_DOUBLE, GRID_LONG = 0, 1, 2, 3


GRID_FLOAT, GRID_INT, GRID_DOUBLE, GRID_LONG = 0, 1, 2, 3


# DataType
class DataType(Enum):
    PER_AVER, PER_CUM, INST_VAL, INST_CUM, FREQ, INVALID = 0, 1, 2, 3, 4, 5


PER_AVER, PER_CUM, INST_VAL, INST_CUM, FREQ, INVALID = 0, 1, 2, 3, 4, 5


# GridStructVersion
class GridStructVersion(Enum):
    VERSION_100 = -100


VERSION_100 = -100

# DssGridType
class DssGridType(Enum):
    UNDEFINED_GRID_TYPE = 400
    HRAP = 410
    ALBERS = 420
    SPECIFIED_GRID_TYPE = 430


UNDEFINED_GRID_TYPE = 400
HRAP = 410
ALBERS = 420
SPECIFIED_GRID_TYPE = 430


# TimeZones
class TimeZone(Enum):
    GMT = UTC = 0
    AST = 4
    EST = 5
    CST = 6
    MST = 7
    PST = 8
    AKST = 9
    HST = 10


GMT = UTC = 0
AST = 4
EST = 5
CST = 6
MST = 7
PST = 8
AKST = 9
HST = 10


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
