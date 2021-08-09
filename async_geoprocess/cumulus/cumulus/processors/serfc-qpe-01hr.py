from datetime import datetime
import os
from ..geoprocess.core.base import info, translate, create_overviews
from ..handyutils.core import change_final_file_extension, gunzip_file
import json

def process(infile, outdir):
    """Takes an infile to process and path to a directory where output files should be saved
    Returns array of objects [{ "filetype": "nohrsc_snodas_swe", "file": "file.tif", ... }, {}, ]
    """
    outfile_list = list()
    fileinfo = info(infile)
    print(fileinfo)
    # with open('/tmp/serfcqpeinfo.txt', 'w') as f:
    #     f.write(json.dumps(fileinfo), indent=4)

    #
    # tif = translate(infile, os.path.join(outdir, f"temp-tif-{uuid4()}"), extra_args=["-b", band_number])
    # tif_with_overviews = create_overviews(tif)
    # cog = translate(
    #     tif_with_overviews,
    #     os.path.join(
    #         outdir,
    #         change_final_file_extension(os.path.basename(infile), 'tif')            
    #     )
    # )

    # outfile_list = [
    #     { "filetype": "serfc-qpe-01h", "file": cog, "datetime": dt.isoformat(), "version": None },
    # ]

    return outfile_list
