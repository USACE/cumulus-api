#!/bin/bash

#
pushd $(dirname $0)

SRCTIFF=/app/async_packager/tiffdss/test/rtma2p5_ru.tif

DSSFILE=DSSFILE.dss
DSSPATH=/SHG/WATERSHED/AIRTEMP/07JUN2022:0015//NCEP-RTMA-RU-ANL/
GRIDTYPE=shg-time
DATATYPE=inst-val
UNITS="DEG C"
TZID=gmt
COMPRESSION=zlib

CELLSIZE=2000


# Warp the tif to Tenn and Cumberland
if [ "$1" == "warp" ]
then
    DSTTIFF=/app/async_packager/tiffdss/test/rtma2p5_ru.tif

    gdalwarp -t_srs "EPSG:5070" -te 642000 1258000 1300000 1682000 \
        -tr ${CELLSIZE} ${CELLSIZE} -r bilinear -overwrite \
        -ot Float64 -tap ${SRCTIFF} ${DSTTIFF}

    SRCTIFF=${DSTTIFF}
fi


# write to dss
./tiffdss ${SRCTIFF} ${DSSFILE} ${DSSPATH} ${GRIDTYPE} \
    ${DATATYPE} ${UNITS} ${TZID} ${COMPRESSION}

popd
