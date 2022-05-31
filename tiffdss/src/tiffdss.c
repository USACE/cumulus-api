#include <stdio.h>
#include <ctype.h>
#include <gdal.h>
#include <math.h>
#include <cpl_string.h>
#include <cpl_conv.h> /* for CPLMalloc() */

#include "heclib.h"

#include "utils.h"

char *to_upper(char *s)
{

    char *s_up = malloc(strlen(s) * sizeof(s));

    for (int i = 0; i < strlen(s) + 1; i++)
    {
        s_up[i] = toupper(s[i]);
    }
    // printf("%s->%s\n", s, s_up);
    return s_up;
}

char *to_lower(char *s)
{
    char *s_up = malloc(strlen(s) * sizeof(s));

    for (int i = 0; i < strlen(s) + 1; i++)
    {
        s_up[i] = tolower(s[i]);
    }
    // printf("%s->%s\n", s, s_up);
    return s_up;
}

int writeRecord(char *filetiff, char *dssfile, char *dsspath,
                char *gridtype, char *datatype, char *units,
                char *tzid, char *compression)
{
    StructGridTypes gridTypes = findGridTypes(to_lower(gridtype));
    int _datatype = findDataType(to_upper(datatype));
    char *_tzid = to_upper(tzid);
    int tzoffset = findTzOffset(_tzid);
    int _compression = findCompressionMethod(compression);

    int interval = 0;
    char pathPart[65];
    int _interval = zpathnameGetPart(dsspath, 5, pathPart, sizeof(pathPart));
    if (_interval == 14)
        interval = 1;
    // printf("Epart(len): %s(%d)\n", pathPart, _interval);
    // printf("Is Interval: %i\n", interval);

    // open the dss file
    long long ifltab[250];
    memset(ifltab, 0, 250 * sizeof(long long));
    int status = zopen(ifltab, dssfile);
    if (status != STATUS_OKAY)
    {
        // printf("Error opeing file: %d\n", status);
        return -1;
    }

    // register the drivers
    GDALAllRegister();

    // get the tiff dataset
    GDALDatasetH hDataset;
    hDataset = GDALOpen(filetiff, GA_ReadOnly);

    // get the raster geotransform
    double adfGeoTransform[6];
    if (GDALGetGeoTransform(hDataset, adfGeoTransform) == CE_None)
    {
        printf("Origin = (%.6f,%.6f)\n",
               adfGeoTransform[0], adfGeoTransform[3]);
        printf("Pixel Size = (%.6f,%.6f)\n",
               adfGeoTransform[1], adfGeoTransform[5]);
    }

    // get the tiff shape
    int xsize = GDALGetRasterXSize(hDataset);
    int ysize = GDALGetRasterYSize(hDataset);
    int dataSize = xsize * ysize;
    float cellsize = adfGeoTransform[1];
    // printf("Xsize: %d\nYsize: %d\nData Size:%d\n", xsize, ysize, dataSize);

    // get raster band 1
    GDALRasterBandH raster = GDALGetRasterBand(hDataset, 1);

    int llx = (int)adfGeoTransform[0] / adfGeoTransform[1];
    int lly = (int)(adfGeoTransform[5] * ysize + adfGeoTransform[3]) / adfGeoTransform[1];
    // printf("Lower Left X: %i\n", llx);
    // printf("Lower Left Y: %i\n", lly);

    // get the tiff data array
    // float *data;
    float *data = (float *)CPLMalloc(sizeof(float) * dataSize);
    // float *data = (float *)CPLMalloc(sizeof(float) * dataSize);
    GDALRasterIO(raster, GF_Read, 0, 0, xsize, ysize, data, xsize, ysize, GDT_Float32, 0, 0);
    // reverse array
    int start = 0;
    int end = dataSize - 1;
    float temp;
    while (start < end)
    {
        temp = data[start];
        data[start] = data[end];
        data[end] = temp;
        start++;
        end--;
    }

    // invert the data
    float *data_ = (float *)CPLMalloc(sizeof(float) * dataSize);

    // get raster statistics
    double pdfMin, pdfMax, pdfMean, pdfStdDev;
    float _min = 0;
    float _max = 0;
    float _mean = 0;
    GDALComputeRasterStatistics(raster, false, &pdfMin, &pdfMax, &pdfMean, &pdfStdDev, NULL, NULL);
    // printf("Raster Stat: min = %f max = %f mean = %f stddev = %f\n", pdfMin, pdfMax, pdfMean, pdfStdDev);
    if (pdfMin != 0.0f)
    {
        // printf("Min Value Not 0, setting to %f\n", pdfMin);
        _min = (float)pdfMin;
    }
    if (pdfMax != 0.0f)
    {
        // printf("Max Value Not 0, setting to %f\n", pdfMax);
        _max = (float)pdfMax;
    }
    if (pdfMean != 0.0f)
    {
        // printf("Mean Value Not 0, setting to %f\n", pdfMean);
        _mean = (float)pdfMean;
    }

    // get no data value
    int valid;
    float noData = 0.0f;
    double _noData = GDALGetRasterNoDataValue(raster, &valid);
    if (valid)
        noData = (float)_noData;

    // printf("No data = %f\n", noData);

    // determine the number of bins for the histogram
    int bins = (int)(1 + 3.322 * log((double)dataSize)) * 0.25f;
    // printf("Histogram bins: %i\n", bins);

    static float *rangelimit;
    static int *histo;
    rangelimit = calloc(bins, sizeof(float));
    histo = calloc(bins, sizeof(float));

    double range = roundf(_max) - floorf(_min);
    // printf("Data range: %f\n", range);

    double step = range / bins;
    // printf("Data step: %f\n", step);

    // range limits
    rangelimit[0] = _min;
    rangelimit[bins - 1] = _max;

    float nextstep;
    for (int i = 1; i < bins - 1; i++)
    {
        nextstep = (float)rangelimit[i - 1] + step;
        rangelimit[i] = floor(pow(10, 2) * nextstep) / pow(10, 2);
    }
    // historgram
    for (int idx = 0; idx < dataSize; idx++)
    {
        // TODO: zero values get no data for precip but what about temperatures
        if (data[idx] == noData)
            data[idx] = UNDEFINED_FLOAT;
        for (int jdx = 0; jdx < bins; jdx++)
        {
            if (data[idx] >= rangelimit[jdx])
                histo[jdx]++;
        }
    }

    // Spatial Grid Struct
    zStructSpatialGrid *gridStructStore = zstructSpatialGridNew(dsspath);
    gridStructStore->_type = gridTypes.gridType;
    gridStructStore->_dataSource = "INTERNAL";
    gridStructStore->_version = 1;
    gridStructStore->_dataUnits = units;
    gridStructStore->_dataType = _datatype;
    gridStructStore->_numberOfCellsX = xsize;
    gridStructStore->_numberOfCellsY = ysize;
    gridStructStore->_lowerLeftCellX = llx;
    gridStructStore->_lowerLeftCellY = lly;
    gridStructStore->_cellSize = cellsize;
    gridStructStore->_compressionMethod = _compression;

    gridStructStore->_rangeLimitTable = &rangelimit[0];
    gridStructStore->_numberEqualOrExceedingRangeLimit = &histo[0];
    gridStructStore->_numberOfRanges = bins;

    gridStructStore->_srsDefinitionType = 1;
    gridStructStore->_srsName = gridTypes.srsName;
    gridStructStore->_srsDefinition = gridTypes.srsDef;
    gridStructStore->_xCoordOfGridCellZero = 0;
    gridStructStore->_yCoordOfGridCellZero = 0;
    gridStructStore->_nullValue = noData;
    gridStructStore->_timeZoneID = _tzid;
    gridStructStore->_timeZoneRawOffset = tzoffset;
    gridStructStore->_isInterval = interval;
    gridStructStore->_isTimeStamped = gridTypes.timeStamp;

    gridStructStore->_minDataValue = &_min;
    gridStructStore->_maxDataValue = &_max;
    gridStructStore->_meanDataValue = &_mean;

    if (data != NULL)
    {
        gridStructStore->_data = data;
        // printGridStruct(ifltab, 0, gridStructStore);
        status = zspatialGridStore(ifltab, gridStructStore);
    }

    GDALClose(hDataset);
    CPLFree(data);

    free(rangelimit);
    free(histo);
    zstructFree(gridStructStore);

    zclose(ifltab);

    return status;
}

void printUsage(char *progname)
{
    fprintf(stderr, "Usage: %s tiff dss dsspath gridtype datatype units tzid cellsize range compression\n",
            progname);
    exit(EXIT_FAILURE);
}

int main(int argc, char *argv[])
{
    char *filetiff = argv[1];
    char *dssfile = argv[2];
    char *dsspath = argv[3];
    char *gridtype = argv[4];
    char *datatype = argv[5];
    char *units = argv[6];
    char *tzid = argv[7];
    char *compression = argv[8];

    for (int i = 1; i < argc; i++)
    {
        if (argv[i] == NULL)
        {
            printUsage(argv[0]);
        }
    }

    int status = writeRecord(filetiff, dssfile, dsspath, gridtype,
                             datatype, units, tzid, compression);

    if (status != STATUS_OKAY)
    {
        printf("Error storing record: %d\n", status);
    }
    else
        printf("Stored record: %s\n", dsspath);
}
