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

void filter_nodata(float *arr, int datasize, float nodata)
{
    for (int i = 0; i < datasize; i++)
    {
        if (arr[i] == nodata)
            arr[i] = UNDEFINED_FLOAT;
    }
}

void filter_zeros(float *arr, int datasize, const char *cpart)
{
    char *found = strstr(cpart, "PRECIP");
    if (found != NULL){
        for (int i = 0; i < datasize; i++)
        {
            if (arr[i] == 0)
                arr[i] = UNDEFINED_FLOAT;
        }
    }
}

void reverse_array(float *arr, int zsize)
{
    // rotate the grid
    int start = 0;
    int end = zsize - 1;
    float tmp;
    while (start < end)
    {
        tmp = arr[start];
        arr[start] = arr[end];
        arr[end] = tmp;
        start++;
        end--;
    }
}

void reverse_rows(float *arr, int cols, int datasize)
{
    int i, j, k = 0;
    int start, end;
    float tmp;

    for (i = 0; i < datasize; i += cols)
    {
        // flip in arrpart
        start = i;
        end = i + cols - 1;
        while (start < end)
        {
            tmp = arr[end];
            arr[end] = arr[start];
            arr[start] = tmp;
            start++;
            end--;
        }
    }
}
