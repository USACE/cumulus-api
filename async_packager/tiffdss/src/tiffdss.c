#include <ctype.h>
#include <gdal.h>
#include <math.h>
#include <cpl_string.h>
#include <cpl_conv.h> /* for CPLMalloc() */

#include "heclib.h"
#include "zdssMessages.h"

#include "utils.h"



// int writeRecord(long long *ifltab, float *data, size_t n)
// int writeRecord(long long *ifltab)
// int writeRecord()
int writeRecord(long long *ifltab, zStructSpatialGrid *gridStructStore, float *data, int n, GridStats *gridStats)
{
    int i, status;

    // determine the number of bins for the histogram
    int bins = (int)(1 + 3.322 * log((double)n)) * 0.25f;
    printf("Histogram bins: %i\n", bins);

    static float *rangelimit;
    static int *histo;
    rangelimit = calloc(bins, sizeof(float));
    histo = calloc(bins, sizeof(float));

    // min = minimum(data, n);
    // max = maximum(data, n);
    // mean = meanvalue(data, n);
    float min = gridStats->minimum;
    float max = gridStats->maximum;
    float mean = gridStats->meanval;

    printf("Min, Max, Mean: %f, %f, %f\n", min, max, mean);
    
    float range = roundf(max) - floorf(min);
    printf("Data range: %f\n", range);

    float step = range / bins;
    printf("Data step: %f\n", step);

    // range limits
    rangelimit[0] = min;
    rangelimit[bins - 1] = max;

    float nextstep;
    for (i = 1; i < bins - 1; i++)
    {
        nextstep = (float)rangelimit[i - 1] + step;
        rangelimit[i] = floor(pow(10, 2) * nextstep) / pow(10, 2);
    }
    // historgram
    for (int idx = 0; idx < n; idx++)
    {
        for (int jdx = 0; jdx < bins; jdx++)
        {
            if (data[idx] >= rangelimit[jdx])
                histo[jdx]++;
        }
    }

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

    status = zspatialGridStore(ifltab, spatialGridStruct);

    free(rangelimit);
    free(histo);
    free(data);

    zstructFree(spatialGridStruct);
    zstructFree(gridStructStore);
    zstructFree(gridStats);

    return status;
}




int main(int argc, char *argv[]){}
