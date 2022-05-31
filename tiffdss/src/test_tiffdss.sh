#!/bin/bash

if [ "$1" == "make" ]
then
    clear
    make clean
    make
fi


SRCTIFF=/newfile.tif
# SRCTIFF=/blend.20210524.t16z.core.f033.co.tif
# SRCTIFF=/MRMS_MultiSensor_QPE_01H_Pass1_00.00_20201110-020000.tif
# SRCTIFF=/zz_ssmv11036tS__T0001TTNATS2019012705HP001_cloud_optimized.tif

DSSFILE=/tiffdss/newfile.dss
DSSPATH=/a/b/snowdepth/27jan2019:0600/28jan2019:0600/f/
GRIDTYPE=ALBERS
DATATYPE=inst-val
UNITS=degc
TZID=gmt
COMPRESSION=zlib


# Warp the tif to Tenn and Cumberland
if [ "$1" == "warp" ]
then
    DSTTIFF=/newfile.tif

    gdalwarp -t_srs "EPSG:5070" -te 642000 1258000 1300000 1682000 \
        -tr ${CELLSIZE} ${CELLSIZE} -r bilinear -overwrite \
        -ot Float64 -tap ${SRCTIFF} ${DSTTIFF}

    SRCTIFF=${DSTTIFF}
fi


# write to dss
./tiffdss ${SRCTIFF} ${DSSFILE} ${DSSPATH} ${GRIDTYPE} \
    ${DATATYPE} ${UNITS} ${TZID} ${COMPRESSION}
