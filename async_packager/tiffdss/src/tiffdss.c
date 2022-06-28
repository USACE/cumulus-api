#include <ctype.h>
#include <gdal.h>
#include <math.h>
#include <cpl_string.h>
#include <cpl_conv.h> /* for CPLMalloc() */

#include "heclib.h"
#include "zdssMessages.h"

#include "utils.h"

int writeRecord(char *dssfilename, zStructSpatialGrid *gridStructStore, float *data, GridStats *gridStats)
{
    int i, n, status;
    float min = 0;
    float max = 0;
    float mean = 0;

    zsetMessageLevel(MESS_METHOD_GLOBAL_ID, MESS_LEVEL_NONE);

    // long long ifltab[250];
    // memset(ifltab, 0 , 250 * sizeof(long long));
    long long *ifltab = calloc(250, sizeof(long long) * 250);

    n = gridStructStore->_numberOfCellsX * gridStructStore->_numberOfCellsY;

    min = minimum(data, n, gridStructStore->_nullValue);
    max = maximum(data, n, gridStructStore->_nullValue);
    mean = meanvalue(data, n, gridStructStore->_nullValue);
    
    // range limits
    // float min = gridStats->minimum;
    // float max = gridStats->maximum;
    // float mean =gridStats->meanval;
    // if(gridStats->minimum == gridStructStore->_nullValue)
    //     min = 0;
    // if(gridStats->maximum == gridStructStore->_nullValue)
    //     max = 0;
    // if(gridStats->meanval == gridStructStore->_nullValue)
    //     mean = 0;

    // printf("Min, Max, Mean: %f, %f, %f\n", min, max, mean);

    float range = max - min;
    // printf("Data range: %f\n", range);

    int bins = 5;
    if (range == 0)
        bins = 2;

    static float *rangelimit;
    static int *histo;
    rangelimit = calloc(bins, sizeof(float));
    histo = calloc(bins, sizeof(float));

    float step = (float)range / bins;
    // printf("Data step: %f\n", step);

    rangelimit[0] = UNDEFINED_FLOAT;
    rangelimit[1] = min;
    if (step != 0)
    {
        rangelimit[2] = min + step * 2;
        rangelimit[3] = min + step * 3;
        rangelimit[4] = max;
    }
    for (int idx = 0; idx < n; idx++)
    {
        for (int jdx = 0; jdx < bins; jdx++)
        {
            if (data[idx] >= rangelimit[jdx])
                histo[jdx]++;
        }
    }

    // filter no data, reverse, and flip data before assigning to struct
    filter_nodata(data, n, gridStructStore->_nullValue, gridStructStore->pathname);
    // reversing the array values rotates it 180
    reverse_array(data, n);
    // reverse each row to flip <--> 180
    reverse_rows(data, gridStructStore->_numberOfCellsX, n);

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

    spatialGridStruct->_maxDataValue = &max;
    spatialGridStruct->_minDataValue = &min;
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
    zstructFree(gridStats);

    return status;
}




int main(int argc, char *argv[]){}
