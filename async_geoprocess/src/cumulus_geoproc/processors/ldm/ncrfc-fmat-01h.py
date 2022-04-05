"""North Central River Forecast Center

Forecast Mesoscale Analysis Surface Temperature 01Hr
"""


import os
import re
from osgeo import gdal
from datetime import datetime, timezone
from collections import namedtuple
from uuid import uuid4
from cumulus_geoproc.geoprocess.core.base import translate, create_overviews
from cumulus_geoproc.handyutils.core import change_final_file_extension

import pyplugs


# @pyplugs.register
def process(src: str, dst: str, acquirable: str = None):
    """Grid processor

    Parameters
    ----------
    src : str
        path to input file for processing
    dst : str
        path to temporary directory created from worker thread
    acquirable: str
        acquirable slug

    Returns
    -------
    List[dict]
        {
            "filetype": str,         Matching database acquirable
            "file": str,             Converted file
            "datetime": str,         Valid Time, ISO format with timezone
            "version": str           Reference Time (forecast), ISO format with timezone
        }
    """

    ftype = "ncrfc-fmat-01h"

    outfile_list = list()

    gdal.UseExceptions()
    try:
        gribs = gdal.ReadDir(f"/vsitar/{infile}")
    except RuntimeError as err:
        print(f"Error ReadDir: {err}")
        return list()

    for grib in gribs:
        try:
            ds = gdal.Open(f"/vsitar/{infile}/{grib}")
            fileinfo = gdal.Info(ds, format="json")
        except RuntimeError as err:
            print(f"Error: {err}")
            continue
        finally:
            ds = None

        band = fileinfo["bands"][0]
        meta = band["metadata"][""]
        Meta = namedtuple("Meta", meta.keys())(**meta)
        # Compile regex to get times from timestamp
        time_pattern = re.compile(r"\d+")
        valid_time_match = time_pattern.match(Meta.GRIB_VALID_TIME)
        ref_time_match = time_pattern.match(Meta.GRIB_REF_TIME)
        valid_time = (
            datetime.fromtimestamp(int(valid_time_match[0]), timezone.utc).isoformat()
            if valid_time_match
            else None
        )
        ref_time = (
            datetime.fromtimestamp(int(ref_time_match[0]), timezone.utc).isoformat()
            if ref_time_match
            else None
        )

        # Extract Band 0 (QPE); Convert to COG
        root, _ = os.path.splitext(grib)

        tif = translate(
            f"/vsitar/{infile}/{grib}", os.path.join(outdir, f"temp-tif-{uuid4()}")
        )
        tif_with_overviews = create_overviews(tif)
        cog = translate(tif_with_overviews, os.path.join(outdir, "{}.tif".format(root)))
        # Append dictionary object to outfile list
        outfile_list.append(
            {
                "filetype": ftype,
                "file": cog,
                "datetime": valid_time,
                "version": ref_time,
            }
        )

    return outfile_list
