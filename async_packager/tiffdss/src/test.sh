#!/bin/bash

#
pushd $(dirname $0)

SRCTIFF=/dss-test-data/tiff/MRMS_MultiSensor_QPE_01H_Pass1_00.00_20220216-170000.tif

DSSFILE=DSSFILE.dss
DSSPATH=/a/b/precip/16FEB2022:1600/16FEB2022:1700/f/
GRIDTYPE=ALBERS
DATATYPE=inst-val
UNITS=mm
TZID=gmt
COMPRESSION=zlib

CELLSIZE=2000


# Warp the tif to Tenn and Cumberland
if [ "$1" == "warp" ]
then
    DSTTIFF=/dss-test-data/tiff/newfile.tif

    gdalwarp -t_srs "EPSG:5070" -te 642000 1258000 1300000 1682000 \
        -tr ${CELLSIZE} ${CELLSIZE} -r bilinear -overwrite \
        -ot Float64 -tap ${SRCTIFF} ${DSTTIFF}

    SRCTIFF=${DSTTIFF}
fi


# write to dss
./tiffdss ${SRCTIFF} ${DSSFILE} ${DSSPATH} ${GRIDTYPE} \
    ${DATATYPE} ${UNITS} ${TZID} ${COMPRESSION}

popd
