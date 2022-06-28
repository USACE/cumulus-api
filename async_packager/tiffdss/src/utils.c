#include <string.h>


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

float maximum(float *arr, int n, float nodata)
{
    float max = arr[0];
    if (max == nodata)
        max = 0;

    for (int i = 0; i < n; i++){
        if (arr[i] > max)
        {
            if  (arr[i] != nodata)
                 max = arr[i];
        }
    }
    return max;
}

float minimum(float *arr, int n, float nodata)
{
    float min = arr[0];
    if (min == nodata)
        min = 0;

    for (int i = 0; i < n; i++){
        if (arr[i] < min)
        {
            if (arr[i] != nodata)
                min = arr[i];
        }    
}
    return min;
}

float meanvalue(float *arr, int n, float nodata)
{
    int count = 0;
    float sum = 0;
    float mean = 0;
    for (int i = 0; i < n; i++)
    {    
        if (arr[i] != nodata)
            {
                sum += arr[i];
                count++;
            }
    }
    if (count > 0)
        mean = sum / count;
    return mean;
}

void filter_nodata(float *arr, int datasize, float nodata, char *cpart)
{
    // char *pos = strstr(cpart, "PRECIP");
    int pos = zfindString(cpart,strlen(cpart),"PRECIP",6);

    for (int i = 0; i < datasize; i++)
    {
        if (arr[i] == nodata)
        {   
             arr[i] = UNDEFINED_FLOAT;
             if (pos >= 0)
             {
                arr[i] = 0.0f;
             }
        }
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
