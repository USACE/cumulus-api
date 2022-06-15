typedef struct
{
    /* data */
    float minimum;
    float maximum;
    float meanval;
}GridStats;


void reverse_array(float *arr, int zsize);
void reverse_rows(float *arr, int cols, int datasize);
void filter_zeros(float *arr, int datasize, const char *cpart);
void filter_nodata(float *arr, int datasize, float nodata);
int opendss(long long *ifltab, const char *dssfile);
int closedss(long long *ifltab);
float maximum(float *arr, int n);
float minimum(float *arr, int n);
float meanvalue(float *arr, int n);
