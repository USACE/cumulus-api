from datetime import datetime
import os
from uuid import uuid4
from ..geoprocess.core.base import info, translate, create_overviews
from ..handyutils.core import change_final_file_extension


def process(infile, outdir):
    """Takes an infile to process and path to a directory where output files should be saved
    Returns array of objects [{ "filetype": "nohrsc_snodas_swe", "file": "file.tif", ... }, {}, ]
    """

    # Only Get Air Temperature to Start; Band 3 (i.e. array position 2 because zero-based indexing)
    dtStr = info(infile)['bands'][2]["metadata"][""]['GRIB_VALID_TIME']
    print(dtStr)
    # Get Datetime from String Like "1599008400 sec UTC"
    dt = datetime.fromtimestamp(int(dtStr.split(" ")[0]))

    # Extract Band 3 (Temperature); Convert to COG
    tif = translate(
        infile,
        os.path.join(outdir, f"temp-tif-{uuid4()}"),
        extra_args=["-b", "3"]
    )
    tif_with_overviews = create_overviews(tif)
    cog = translate(
        tif_with_overviews,
        os.path.join(
            outdir,
            "{}_{}".format(
                dt.strftime("%Y%m%d"),
                change_final_file_extension(infile, 'tif')
            )
        )
    )

    outfile_list = [
        { "filetype": "ncep-rtma-ru-anl-airtemp", "file": cog, "datetime": dt.isoformat(), "version": None },
    ]

    return outfile_list
