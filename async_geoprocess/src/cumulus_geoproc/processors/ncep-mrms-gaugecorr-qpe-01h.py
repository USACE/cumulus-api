"""_summary_
"""


from datetime import datetime, timezone
import os
from uuid import uuid4
from cumulus_geoproc.geoprocess.core.base import info, translate, create_overviews
import pyplugs


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

    # Only Get Air Temperature to Start; Band 3 (i.e. array position 2 because zero-based indexing)
    dtStr = info(f"/vsigzip/{infile}")["bands"][0]["metadata"][""]["GRIB_VALID_TIME"]

    # Get Datetime from String Like "1599008400 sec UTC"
    dt = datetime.fromtimestamp(int(dtStr.split(" ")[0]))

    # Extract Band 3 (Temperature); Convert to COG
    tif = translate(f"/vsigzip/{infile}", os.path.join(outdir, f"temp-tif-{uuid4()}"))
    tif_with_overviews = create_overviews(tif)
    cog = translate(
        tif_with_overviews,
        os.path.join(
            outdir, "{}.tif".format(os.path.basename(infile).split(".grib2.gz")[0])
        ),
    )

    outfile_list = [
        {
            "filetype": "ncep-mrms-gaugecorr-qpe-01h",
            "file": cog,
            "datetime": dt.replace(tzinfo=timezone.utc).isoformat(),
        },
    ]

    return outfile_list
