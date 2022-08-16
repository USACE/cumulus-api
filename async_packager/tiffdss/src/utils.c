#include <string.h>
#include <math.h>

#include "heclib.h"
#include "utils.h"
#include "zdssMessages.h"

int opendss(long long *ifltab, const char *dssfile)
{
    zsetMessageLevel(MESS_METHOD_GLOBAL_ID, MESS_LEVEL_INTERNAL_DIAG_1);
    return zopen7(ifltab, dssfile);
}

int closedss(long long *ifltab)
{
    return zcloseInternal(ifltab, 0);
}

float roundValue(float var, int precision)
{
    int precision_ = 1 / pow(10, precision);
    float value = (int)(var / precision_ + 0.5);
    return (float)value * precision_;
}

void rangelimit_table(float minval, float maxval, int range, int bins, int datasize, float *rangelimit, int *histo, float *data)
{
    float step = (float)range / bins;

    int i = 0;
    rangelimit[i] = UNDEFINED_FLOAT;
    rangelimit[i + 1] = minval;
    for (i = 2; i < bins - 1; i++)
    {
        if (step != 0)
            rangelimit[i] = minval + step * i;
    }
    rangelimit[i] = maxval;

    // Exceedance
    for (int idx = 0; idx < datasize; idx++)
    {
        for (int jdx = 0; jdx < bins; jdx++)
        {
            if (data[idx] >= rangelimit[jdx])
                histo[jdx]++;
        }
    }
}

float maximum(float *arr, int n, float nodata)
{
    float max = -2.0E38F;

    for (int i = 0; i < n; i++)
    {
        if (arr[i] != nodata && arr[i] > max)
            max = arr[i];
    }

    return max;
}

float minimum(float *arr, int n, float nodata)
{
    float min = 2.0E38F;

    for (int i = 0; i < n; i++)
    {
        if (arr[i] != nodata && arr[i] < min)
            min = arr[i];
    }

    return min;
}

float meanvalue(float *arr, int n, float nodata)
{
    int count = 1;
    float sum = arr[0];
    float mean = UNDEFINED_FLOAT;

    for (int i = 1; i < n; i++)
    {
        if (arr[i] != nodata && sum > UNDEFINED_FLOAT)
        {
            sum += arr[i];
            count++;
        }
    }
    mean = sum / count;
    return mean;
}

void filter_nodata(float *arr, int datasize, float nodata)
{
    for (int i = 0; i < datasize; i++)
    {
        // dif = fabs(arr[i] - nodata);
        if (arr[i] == nodata)
        {
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

int dssDataType(const char *dType)
{
    if (strcmp(dType, "PER-AVER") == 0)
        return PER_AVER;
    if (strcmp(dType, "PER-CUM") == 0)
        return PER_CUM;
    if (strcmp(dType, "INST-VAL") == 0)
        return INST_VAL;
    if (strcmp(dType, "INST-CUM") == 0)
        return INST_CUM;
    if (strcmp(dType, "FREQ") == 0)
        return FREQ;
    return -1;
}

int dssCompressionMethod(const char *compressMethod)
{
    if (strcmp(compressMethod, "undefined") == 0)
        return UNDEFINED_COMPRESSION_METHOD;
    if (strcmp(compressMethod, "zlib") == 0)
        return ZLIB_COMPRESSION;
    return -1;
}

int dssGridType(const char *gtype)
{
    if (strcmp(gtype, "UNDEFINED_GRID_TYPE") == 0)
        return 400;
    if (strcmp(gtype, "HRAP") == 0)
        return 410;
    if (strcmp(gtype, "ALBERS") == 0 || strcmp(gtype, "SHG") == 0)
        return 420;
    if ((strcmp(gtype, "SPECIFIED_GRID_TYPE") == 0) || (strcmp(gtype, "UTM") == 0))
        return 430;
    return -1;
}

int tzOffset(const char *tz)
{
    if (tz == NULL)
        return -1;
    if ((strcmp(tz, "GMT") == 0) || (strcmp(tz, "UTC") == 0))
        return 0;
    if (strcmp(tz, "AST") == 0)
        return 4;
    if (strcmp(tz, "EST") == 0)
        return 5;
    if (strcmp(tz, "CST") == 0)
        return 6;
    if (strcmp(tz, "MST") == 0)
        return 7;
    if (strcmp(tz, "PST") == 0)
        return 8;
    if (strcmp(tz, "AKST") == 0)
        return 9;
    if (strcmp(tz, "HST") == 0)
        return 10;
    return -1;
}

char *dssGridDef(int gtype)
{
    switch (gtype)
    {
    case 400:
        return NULL;
    case 410:
        return HRAP_SRC_DEFINITION;
    case 420:
        return SHG_SRC_DEFINITION;
    case 430:
        return NULL;
    default:
        return NULL;
    }
}

char *utmGridDef(int zone, char *utmHemi)
{
    char *falseNorthing = "0";
    char _centralMeridian[sizeof(int)];
    char tens[sizeof(int)];
    char ones[sizeof(int)];
    int len = sizeof(UTM_SRC_DEFINITION);
    char *utm = (char *)malloc(sizeof(char) * len);

    if (strcmp(utmHemi, "S") == 0)
        falseNorthing = "10000000";
    int centralMeridian = -183 + zone * 6;

    snprintf(_centralMeridian, sizeof(int), "%d", centralMeridian);
    snprintf(tens, sizeof(int), "%.f", fmodf(zone, 10));
    snprintf(ones, sizeof(int), "%d", zone / 10);

    snprintf(utm, len, UTM_SRC_DEFINITION, ones, tens, _centralMeridian, falseNorthing);

    return utm;
}
