from fileinput import filename
import subprocess
import os
from tempfile import TemporaryDirectory
import numpy as np
import numpy.ma as ma
from osgeo import gdal
from affine import Affine
import config as CONFIG
import traceback
from pathlib import Path

from pydsstools.heclib.dss.HecDss import Open
from pydsstools.heclib.utils import gridInfo, setMessageLevel

gdal.UseExceptions()


def writer(outfile, extent, items, callback, cellsize=2000, dst_srs="EPSG:5070"):
    """
    DSS output level
    Message Levels for individual methods (operation):  #
    0:	No messages, including error (not guaranteed).  Highly discourage
    1:	Critical (Error) Messages.  Discouraged.
    2:	Minimal (terse) output:  zopen, zclose, critical errors.
    3:	General Log Messages.  Default.
    4:	Diagnostic User Messages (e.g., input parameters)
    5:	Diagnostic Internal Messages level 1 (debug).   Not recommended for users
    6:	Diagnostic Internal Messages level 2 (full debug)
    Note:  Levels 1-3 are for Unicode.  Level 4+ is ASCII (hardwired)

    Compatibility for version 6 MLVL with no method set (general)
    0:	No messages, including error (not guaranteed).  Highly discourage
    1:	Critical (Error) Messages.  Discouraged
    2:	Minimal (terse) output:  zopen, zclose, critical errors.
    3:	General Log Messages: zwrites.  Default.
    4:	Log messages, including zread
    10:	Diagnostic User Messages (e.g., input parameters)
    12:	Diagnostic Internal Messages level 1 (debug).   Not recommended for users
    15:	Diagnostic Internal Messages level 2 (full debug



    outfile = dssfile to write to
    extent = has the bbox
    items = list of items with source tiff and dss paramters

    """
    if CONFIG.PACKAGER_LOG_LEVEL == "DEBUG":
        setMessageLevel(methodID=6, levelID=15)
    elif CONFIG.PACKAGER_LOG_LEVEL == "INFO":
        setMessageLevel(methodID=3, levelID=3)
    else:
        setMessageLevel(methodID=1, levelID=1)

    dst = os.path.dirname(outfile)

    item_length = len(items)
    for idx, item in enumerate(items):
        print(f"\n\nIndex {idx}; Item {item}")
        try:
            # Update progress at predefined interval
            if idx % CONFIG.PACKAGER_UPDATE_INTERVAL == 0 or idx == item_length - 1:
                callback(idx)

            with TemporaryDirectory(dir=dst) as td:
                # with TemporaryDirectory() as td:
                bucket = item["bucket"]
                key = item["key"]
                filename_ = os.path.basename(key)
                print(f"{filename_=}")

                ds = gdal.Open(f"/vsis3_streaming/{bucket}/{key}")
                print(f"XSize: {ds.RasterXSize}")
                print(f"YSize: {ds.RasterYSize}")

                gdal.Warp(
                    tmptiff := f"/tmp/{filename_}",
                    ds,
                    format="GTiff",
                    outputBounds=extent["bbox"],
                    xRes=cellsize,
                    yRes=cellsize,
                    targetAlignedPixels=True,
                    # srcSRS=None,
                    dstSRS=dst_srs,
                    outputType=gdal.GDT_Float64,
                    resampleAlg="bilinear",
                    dstNodata=-9999,
                    copyMetadata=False,
                )

                print(f"{tmptiff=}")
                """
                    char *filetiff = argv[1];
                    char *dssfile = argv[2];
                    char *dsspath = argv[3];
                    char *gridtype = argv[4];
                    char *datatype = argv[5];
                    char *units = argv[6];
                    char *tzid = argv[7];
                    char *compression = argv[8];
                """
                cmd = "/app/packager/tiffdss"
                cmd += " " + tmptiff
                cmd += " /tmp/download_dss.dss"
                cmd += f' "/SHG/{extent["name"]}/{item["dss_cpart"]}/{item["dss_dpart"]}/{item["dss_epart"]}/{item["dss_fpart"]}/"'
                cmd += " shg-time"
                cmd += " " + item["dss_datatype"]
                cmd += " " + item["dss_unit"]
                cmd += " gmt"
                cmd += " zlib"

                print("*" * 20, f"CMD: {cmd}")
                sp = subprocess.check_call(cmd, cwd="/app/packager", shell=True)
                print(f"{sp=}")

        except Exception as ex:
            print(ex)
            # print(f'Unable to process: {item["bucket"]}/{item["key"]}')
            # print(traceback.print_exc())
        finally:
            ds = None

    return os.path.abspath(outfile)


if __name__ == "__main__":
    pass
