#include <stdio.h>
#include <string.h>

#include "heclib.h"
#include "utils.h"

StructGridTypes findGridTypes(const char *gridType)
{
    StructGridTypes s;

    int grid_type;
    if (strcmp(gridType, "shg") == 0 || strcmp(gridType, "albers") == 0)
    {
        s.gridType = ALBERS;
        s.timeStamp = 0;
        s.srsDef = SHG_SRC_DEFINITION;
        s.srsName = "ALBERS";
    }
    else if (strcmp(gridType, "shg-time") == 0 || strcmp(gridType, "albers-time") == 0)
    {
        s.gridType = ALBERS;
        s.timeStamp = 1;
        s.srsDef = SHG_SRC_DEFINITION;
        s.srsName = "ALBERS";
    }
    else if (strcmp(gridType, "hrap") == 0)
    {
        s.gridType = HRAP;
        s.timeStamp = 0;
        s.srsDef = HRAP_SRC_DEFINITION;
        s.srsName = "HRAP";
    }
    else if (strcmp(gridType, "hrap-time") == 0)
    {
        s.gridType = HRAP;
        s.timeStamp = 1;
        s.srsDef = HRAP_SRC_DEFINITION;
        s.srsName = "HRAP";
    }
    return s;
}

int findDataType(const char *dType)
{
    if (strcmp(dType, "PER-AVER") == 0)
    {
        return PER_AVER;
    }
    else if (strcmp(dType, "PER-CUM") == 0)
    {
        return PER_CUM;
    }
    else if (strcmp(dType, "INST-VAL") == 0)
    {
        return INST_VAL;
    }
    else if (strcmp(dType, "INST-CUM") == 0)
    {
        return INST_CUM;
    }
    else if (strcmp(dType, "FREQ") == 0)
    {
        return FREQ;
    }
    else
    {
        return -1;
    }
}

int findCompressionMethod(const char *compressMethod)
{
    int result;
    if (strcmp(compressMethod, "undefined") == 0)
    {
        result = UNDEFINED_COMPRESSION_METHOD;
    }
    else if (strcmp(compressMethod, "zlib") == 0)
    {
        result = ZLIB_COMPRESSION;
    }
    else
    {
        result - 1;
    }
    return result;
}

int findTzOffset(const char *tz)
{
    if (strcmp(tz, "GMT") == 0 || strcmp(tz, "UTC") == 0)
    {
        return GMT;
    }
    else if (strcmp(tz, "AST") == 0)
    {
        return AST;
    }
    else if (strcmp(tz, "EST") == 0)
    {
        return EST;
    }
    else if (strcmp(tz, "CST") == 0)
    {
        return CST;
    }
    else if (strcmp(tz, "MST") == 0)
    {
        return MST;
    }
    else if (strcmp(tz, "PST") == 0)
    {
        return PST;
    }
    else if (strcmp(tz, "AKST") == 0)
    {
        return AKST;
    }
    else if (strcmp(tz, "HST") == 0)
    {
        return HST;
    }
}
