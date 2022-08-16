#include <ctype.h>
#include <gdal.h>
#include <math.h>
#include <cpl_string.h>
#include <cpl_conv.h> /* for CPLMalloc() */

#include "heclib.h"
#include "zdssMessages.h"

#include "utils.h"

int writeRecord(char *dssfilename, zStructSpatialGrid *gridStructStore, float *data)
{
    int i, n, status;
    float minval = 0;
    float maxval = 0;
    float mean = 0;

    zsetMessageLevel(MESS_METHOD_GLOBAL_ID, MESS_LEVEL_NONE);

    // long long ifltab[250];
    // memset(ifltab, 0 , 250 * sizeof(long long));
    long long *ifltab = calloc(250, sizeof(long long) * 250);

    n = gridStructStore->_numberOfCellsX * gridStructStore->_numberOfCellsY;

    minval = minimum(data, n, gridStructStore->_nullValue);
    maxval = maximum(data, n, gridStructStore->_nullValue);
    mean = meanvalue(data, n, gridStructStore->_nullValue);

    // filter no data values to UNDEFINE_FLOAT
    filter_nodata(data, n, gridStructStore->_nullValue);
    // reversing the array values rotates it 180
    reverse_array(data, n);
    // reverse each row to flip <--> 180
    reverse_rows(data, gridStructStore->_numberOfCellsX, n);

    // get the rangelimit table and histogram
    int bin_range = (int)(ceil(maxval) - floor(minval));
    int bins = 3;
    if (bin_range > 0)
        bins = floor(1 + 3.322 * log10(n) + 1);

    static float *rangelimit;
    static int *histo;
    rangelimit = calloc(bins, sizeof(float));
    histo = calloc(bins, sizeof(float));

    // populate the rangelimit and histogram
    rangelimit_table(minval, maxval, bin_range, bins, n, rangelimit, histo, data);

    zStructSpatialGrid *spatialGridStruct = zstructSpatialGridNew(gridStructStore->pathname);

    spatialGridStruct->_type = gridStructStore->_type;
    spatialGridStruct->_version = gridStructStore->_version;
    spatialGridStruct->_dataUnits = gridStructStore->_dataUnits;
    spatialGridStruct->_dataType = gridStructStore->_dataType;
    spatialGridStruct->_dataSource = gridStructStore->_dataSource;
    spatialGridStruct->_lowerLeftCellX = gridStructStore->_lowerLeftCellX;
    spatialGridStruct->_lowerLeftCellY = gridStructStore->_lowerLeftCellY;
    spatialGridStruct->_numberOfCellsX = gridStructStore->_numberOfCellsX;
    spatialGridStruct->_numberOfCellsY = gridStructStore->_numberOfCellsY;
    spatialGridStruct->_cellSize = gridStructStore->_cellSize;
    spatialGridStruct->_compressionMethod = gridStructStore->_compressionMethod;

    spatialGridStruct->_rangeLimitTable = &(rangelimit[0]);
    spatialGridStruct->_numberEqualOrExceedingRangeLimit = &(histo[0]);
    spatialGridStruct->_numberOfRanges = bins;

    spatialGridStruct->_srsDefinitionType = gridStructStore->_srsDefinitionType;
    spatialGridStruct->_srsName = gridStructStore->_srsName;
    spatialGridStruct->_srsDefinition = gridStructStore->_srsDefinition;
    spatialGridStruct->_xCoordOfGridCellZero = gridStructStore->_xCoordOfGridCellZero;
    spatialGridStruct->_yCoordOfGridCellZero = gridStructStore->_yCoordOfGridCellZero;
    spatialGridStruct->_nullValue = gridStructStore->_nullValue;
    spatialGridStruct->_timeZoneID = gridStructStore->_timeZoneID;
    spatialGridStruct->_timeZoneRawOffset = gridStructStore->_timeZoneRawOffset;
    spatialGridStruct->_isInterval = gridStructStore->_isInterval;
    spatialGridStruct->_isTimeStamped = gridStructStore->_isTimeStamped;

    spatialGridStruct->_maxDataValue = &maxval;
    spatialGridStruct->_minDataValue = &minval;
    spatialGridStruct->_meanDataValue = &mean;
    spatialGridStruct->_data = data;

    status = zopen7(ifltab, dssfilename);
    status = zspatialGridStore(ifltab, spatialGridStruct);
    status = zclose(ifltab);

    free(rangelimit);
    free(histo);

    free(ifltab);

    zstructFree(spatialGridStruct);
    zstructFree(gridStructStore);

    return status;
}

int zStructSpatialGridDefine(zStructSpatialGrid *gridStructStore, char *tiff, char *dssfile, char *dsspath,
                             char *gridType, int dss_grid_type, char *gridDef, char *dataType,
                             int dss_data_type, char *units, char *tzname, int tzoffset,
                             int compression_method, int timestamped, float nodata, int flip_rotate)
{
    // see if the record is_interval
    int interval = 0;
    char pathPart[65];
    int _interval = zpathnameGetPart(dsspath, 5, pathPart, sizeof(pathPart));
    if (_interval == 14)
        interval = 1;

    // register the drivers
    GDALAllRegister();

    // get the tiff dataset
    GDALDatasetH hDataset;
    hDataset = GDALOpen(tiff, GA_ReadOnly);

    // get the raster geotransform
    double adfGeoTransform[6];
    GDALGetGeoTransform(hDataset, adfGeoTransform);

    // get the tiff shape
    int xsize = GDALGetRasterXSize(hDataset);
    int ysize = GDALGetRasterYSize(hDataset);
    int dataSize = xsize * ysize;
    float cellsize = adfGeoTransform[1];

    // get raster band 1
    GDALRasterBandH raster = GDALGetRasterBand(hDataset, 1);

    int llx = (int)adfGeoTransform[0] / adfGeoTransform[1];
    int lly = (int)(adfGeoTransform[5] * ysize + adfGeoTransform[3]) / adfGeoTransform[1];
    // printf("Lower Left X: %i\n", llx);
    // printf("Lower Left Y: %i\n", lly);

    // get the tiff data array
    float *data = (float *)CPLMalloc(sizeof(float) * dataSize);
    GDALRasterIO(raster, GF_Read, 0, 0, xsize, ysize, data, xsize, ysize, GDT_Float32, 0, 0);

    // reversing the array values rotates it 180
    if (flip_rotate == 1 || flip_rotate == 3)
        reverse_array(data, dataSize);

    // reverse each row to flip <--> 180
    if (flip_rotate == 2 || flip_rotate == 3)
        reverse_rows(data, gridStructStore->_numberOfCellsX, dataSize);

    // Spatial Grid Struct
    gridStructStore->_type = dss_grid_type;
    gridStructStore->_dataSource = "INTERNAL";
    gridStructStore->_version = 1;
    gridStructStore->_dataUnits = units;
    gridStructStore->_dataType = dss_data_type;
    gridStructStore->_numberOfCellsX = xsize;
    gridStructStore->_numberOfCellsY = ysize;
    gridStructStore->_lowerLeftCellX = llx;
    gridStructStore->_lowerLeftCellY = lly;
    gridStructStore->_cellSize = cellsize;
    gridStructStore->_compressionMethod = compression_method;

    gridStructStore->_srsDefinitionType = 1;
    gridStructStore->_srsName = gridType;
    gridStructStore->_srsDefinition = gridDef;
    gridStructStore->_xCoordOfGridCellZero = 0;
    gridStructStore->_yCoordOfGridCellZero = 0;
    gridStructStore->_nullValue = nodata;
    gridStructStore->_timeZoneID = tzname;
    gridStructStore->_timeZoneRawOffset = tzoffset;
    gridStructStore->_isInterval = interval;
    gridStructStore->_isTimeStamped = timestamped;
    gridStructStore->_data = data;

    return 0;
}

void printUsage(char *name)
{
    printf("usage: %s  -p [-c] [-d] [-f] [-g] [-h] [-l] [-m] [-n] [-s] [-u] [-v] [-z]\n"
           "\t-c: DSS compression method; UNDEFINED_COMPRESSION_METHOD or ZLIB_COMPRESSION (default: ZLIB_COMPRESSION)\n"
           "\t-d: DSS data type; PER-AVER | PER-CUM | INST-VAL | INST-CUM (default: PER-AVER)\n"
           "\t-f: Flip options, 0 - no flip; 1 - flip up/down; 2 - flip left/right; 3 - flip up/down and left/right (default: 0)"
           "\t-g: DSS grid type; HRAP | ALBERS | SHG | SPECIFIED_GRID_TYPE | UTM (default: ALBERS)\n"
           "\t-h: Hemisphere N or S; use with -g UTM (default: N)\n"
           "\t-l: zsetMessageLevel (default: 0 (None))\n"
           "\t-m: No data value (default: 9999)\n"
           "\t-n: Time zone name (default: GMT)\n"
           "\t-p: DSS pathname\n"
           "\t-s: DSS grid record time stamped; 0 | 1 (default: 1)\n"
           "\t-u: DSS grid record units (default: MM)\n"
           "\t-v: Verbose; print some output\n"
           "\t-z: UTM Zone 1-60; use with -g UTM\n"
           "<input_Tiff> <output_DSS>\n",
           name);
    exit(0);
}

int main(int argc, char *argv[])
{
    int opt;
    int utmZone = 60;
    int status;
    int tzoffset = 0;
    int timestamped = 1;
    int lvl = 0;
    int flip_rotate = 0;

    bool verbose = false;

    float nodata = 9999;

    char *dataType = "PER-AVER";
    char *gridType = "ALBERS";
    char *gridDef = SHG_SRC_DEFINITION;
    char *tiff;
    char *dssfile;
    char *dsspath = "///////";
    char *units = "MM";
    char *hemisphere = "N";
    char *tzname = "GMT";
    char *compressionMethod = "zlib";

    if (argc < 2)
    {
        printUsage(argv[0]);
    }

    while ((opt = getopt(argc, argv, ":c:d:fg:h:l:m:n:p:su:vz:")) != -1)
    {
        switch (opt)
        {
        case 'c':
            compressionMethod = optarg;
            break;
        case 'd':
            dataType = optarg;
            break;
        case 'f':
            flip_rotate = atoi(optarg);
            break;
        case 'g':
            gridType = optarg;
            break;
        case 'h':
            hemisphere = optarg;
            break;
        case 'l':
            lvl = atoi(optarg);
            break;
        case 'm':
            nodata = atoi(optarg);
            break;
        case 'n':
            tzname = optarg;
            break;
        case 'p':
            dsspath = optarg;
            break;
        case 's':
            timestamped = 0;
            break;
        case 'u':
            units = optarg;
            break;
        case 'v':
            verbose = true;
        case 'z':
            utmZone = atoi(optarg);
            if (utmZone < 1 || utmZone > 60)
            {
                printf("UTM Zones: 1-60 but %i was given\n", utmZone);
                printUsage(argv[0]);
            }
            break;
        case ':':
            printf("option needs a value\n");
            printUsage(argv[0]);
            break;
        case '?':
            if (optopt == opt)
            {
                fprintf(stderr, "Option -%c requires an argument.\n", optopt);
            }
            else if (isprint(optopt))
            {
                fprintf(stderr, "Unknown option `-%c'.\n", optopt);
            }
            else
            {
                fprintf(stderr, "Unknown option character `\\x%x'.\n", optopt);
            }
            return 1;
        default:
            abort();
        }
    }
    // set DSS message level
    zsetMessageLevel(MESS_METHOD_GLOBAL_ID, lvl);

    // check dsspath
    if (strcmp(dsspath, "///////") == 0)
    {
        printf("Define DSS pathname parts: %s\n", dsspath);
        return -1;
    }

    // get the time zone offset
    tzoffset = tzOffset(tzname);

    // get the grid definition
    int dss_grid_type = dssGridType(gridType);
    gridDef = dssGridDef(dss_grid_type);

    // get the data type
    int dss_data_type = dssDataType(dataType);

    int compression_method = dssCompressionMethod(compressionMethod);

    // define UTM grid definition
    if (dss_grid_type == 430)
    {
        gridDef = utmGridDef(utmZone, hemisphere);
        if (verbose)
        {
            printf("Hemisphere: %s", hemisphere);
            printf("UTM Def: %s", gridDef);
        }
    }

    // last two non-optional arguments are input file (tiff) output file (dss)
    tiff = argv[argc - 2];
    dssfile = argv[argc - 1];

    if (verbose)
    {
        printf("DSS pathname: %s\n", dsspath);
        printf("Time Zone Name [offset]: %s[%d]\n", tzname, tzoffset);
        printf("DSS Grid Type: %s[%d]\n", gridType, dss_grid_type);
        printf("DSS data type[type]: %s[%d]\n", dataType, dss_data_type);
        printf("Compression method [val]: %s[%d]\n", compressionMethod, compression_method);
        printf("Tiff file: %s\n", tiff);
        printf("DSS file: %s\n", dssfile);
    }

    // Create a SpatialGridStruct and populate
    zStructSpatialGrid *gridStructStore = zstructSpatialGridNew(dsspath);

    status = zStructSpatialGridDefine(gridStructStore, tiff, dssfile, dsspath, gridType, dss_grid_type,
                                      gridDef, dataType, dss_data_type, units, tzname, tzoffset,
                                      compression_method, timestamped, nodata, flip_rotate);

    if (status != STATUS_OKAY)
    {
        printf("Spatial Grid Struct Error: %d\n", status);
        return -1;
    }

    // Write to DSS record
    status = writeRecord(dssfile, gridStructStore, gridStructStore->_data);

    if (status != STATUS_OKAY)
    {
        printf("Write Record: %d\n", status);
        return -1;
    }

    return 1;
}
