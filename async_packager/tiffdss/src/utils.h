enum DssGridType
{
    UNDEFINED_GRID_TYPE = 400,
    HRAP = 410,
    ALBERS = 420,
    SPECIFIED_GRID_TYPE = 430
};

typedef struct
{
    int gridType, timeStamp;
    char *srsName, *srsDef;
} StructGridTypes;

enum TimeZones
{
    GMT = 0,
    UTC = 0,
    AST = 4,
    EST = 5,
    CST = 6,
    MST = 7,
    PST = 8,
    AKST = 9,
    HST = 10
};

StructGridTypes findGridTypes(const char *gridType);

int findDataType(const char *dataType);

int findCompressionMethod(const char *compressMethod);

int findTzOffset(const char *tz);
