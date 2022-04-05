"""WPC QPF 2.5km
"""


from datetime import datetime, timezone
import os
from uuid import uuid4
from cumulus_geoproc.geoprocess.core.base import info, translate, create_overviews
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

    # Date String
    dtStr = info(infile)["bands"][0]["metadata"][""]["GRIB_VALID_TIME"]
    # Get Datetime from String Like "1599008400 sec UTC"
    dt = datetime.fromtimestamp(int(dtStr.split(" ")[0]))

    # Version (Forecast Issue Time)
    verStr = info(infile)["bands"][0]["metadata"][""]["GRIB_REF_TIME"]
    # Get Datetime from String Like "1599008400 sec UTC"
    vt = datetime.fromtimestamp(int(verStr.split(" ")[0]))

    # Extract Band
    tif = translate(infile, os.path.join(outdir, f"temp-tif-{uuid4()}"))
    tif_with_overviews = create_overviews(tif)
    cog = translate(
        tif_with_overviews,
        os.path.join(
            outdir, "{}.tif".format(os.path.basename(infile).split(".grb")[0])
        ),
    )

    outfile_list = [
        {
            "filetype": "wpc-qpf-2p5km",
            "file": cog,
            "datetime": dt.replace(tzinfo=timezone.utc).isoformat(),
            "version": vt.replace(tzinfo=timezone.utc).isoformat(),
        },
    ]

    return outfile_list
