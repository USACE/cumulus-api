import os
import re
from datetime import datetime, timezone
from collections import namedtuple
from uuid import uuid4
from cumulus_geoproc.geoprocess.core.base import info, translate, create_overviews

import pyplugs


@pyplugs.register
def process(infile, outdir):
    """MRMS MultiSensor QPE 01H Pass2 Caribbean

    Parameters
    ----------
    infile : string
        File to be processed
    outdir : string
        Directory where output files are saved

    Return:
    -------
    list[dict]
        {
            "filetype": string,         Matching database acquirable
            "file": string,             Converted file
            "datetime": string,         Valid Time, ISO format with timezone
            "version": string           Reference Time (forecast), ISO format with timezone
        }
    """

    outfile_list = list()

    # Parse the grid information
    fileinfo = info(f"/vsigzip/{infile}")
    band = fileinfo["bands"][0]
    meta = band["metadata"][""]
    Meta = namedtuple("Meta", meta.keys())(**meta)
    # Compile regex to get times from timestamp
    time_pattern = re.compile(r"\d+")
    valid_time_match = time_pattern.match(Meta.GRIB_VALID_TIME)

    valid_time = (
        datetime.fromtimestamp(int(valid_time_match[0]), timezone.utc).isoformat()
        if valid_time_match
        else ""
    )

    # Extract Band 0 (QPE); Convert to COG
    tif = translate(f"/vsigzip/{infile}", os.path.join(outdir, f"temp-tif-{uuid4()}"))
    tif_with_overviews = create_overviews(tif)
    cog = translate(
        tif_with_overviews,
        os.path.join(
            outdir, "{}.tif".format(os.path.basename(infile).split(".grib2.gz")[0])
        ),
    )
    # Append dictionary object to outfile list
    outfile_list.append(
        {
            "filetype": "ncep-mrms-v12-msqpe01h-p2-carib",
            "file": cog,
            "datetime": valid_time,
            "version": None,
        }
    )

    return outfile_list
