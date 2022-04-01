"""NCEP RTMA Airtemp
"""


from datetime import datetime, timezone
import os
from uuid import uuid4
from cumulus_geoproc.geoprocess.core.base import info, translate, create_overviews
from cumulus_geoproc.handyutils.core import change_final_file_extension

import pyplugs


# @pyplugs.register
def process(infile: str, outdir: str):
    """Grid processor

    Parameters
    ----------
    infile : str
        path to input file for processing
    outdir : str
        path to processor result

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

    # Only Get Air Temperature to Start; Band 3 (i.e. array position 2 because zero-based indexing)
    dtStr = info(infile)["bands"][2]["metadata"][""]["GRIB_VALID_TIME"]

    # Get Datetime from String Like "1599008400 sec UTC"
    dt = datetime.fromtimestamp(int(dtStr.split(" ")[0]))

    # Extract Band 3 (Temperature); Convert to COG
    tif = translate(
        infile, os.path.join(outdir, f"temp-tif-{uuid4()}"), extra_args=["-b", "3"]
    )
    tif_with_overviews = create_overviews(tif)
    cog = translate(
        tif_with_overviews,
        os.path.join(
            outdir,
            "{}_{}".format(
                dt.strftime("%Y%m%d"), change_final_file_extension(infile, "tif")
            ),
        ),
    )

    outfile_list = [
        {
            "filetype": "ncep-rtma-ru-anl-airtemp",
            "file": cog,
            "datetime": dt.replace(tzinfo=timezone.utc).isoformat(),
            "version": None,
        },
    ]

    return outfile_list
