"""Colorado Basin River Forecast Center (CBRFC)

Multisensor Precipitation Estimates (MPE)
"""


import os
from datetime import datetime, timezone
from uuid import uuid4

import pyplugs
from cumulus_geoproc.geoprocess.core.base import create_overviews, info, translate
from cumulus_geoproc.handyutils.core import change_final_file_extension


@pyplugs.register
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
    outfile_list = list()

    fileinfo = info(infile)

    for band in fileinfo["bands"]:
        band_number = str(band["band"])
        band_meta = band["metadata"][""]
        dtStr = band_meta["GRIB_VALID_TIME"]
        if "Total precipitation" in band_meta["GRIB_COMMENT"]:
            break

    # Get Datetime from String Like "1599008400 sec UTC"
    dt = datetime.fromtimestamp(int(dtStr.split(" ")[0]))

    # print(f"Band number is {band_number}, date string is {dtStr}, and date is {dt}")

    # # Extract Band 0 (QPE); Convert to COG
    tif = translate(
        infile,
        os.path.join(outdir, f"temp-tif-{uuid4()}"),
        extra_args=["-b", band_number],
    )
    tif_with_overviews = create_overviews(tif)
    cog = translate(
        tif_with_overviews,
        os.path.join(
            outdir, change_final_file_extension(os.path.basename(infile), "tif")
        ),
    )

    outfile_list = [
        {
            "filetype": "cbrfc-mpe",
            "file": cog,
            "datetime": dt.replace(tzinfo=timezone.utc).isoformat(),
            "version": None,
        },
    ]

    return outfile_list
