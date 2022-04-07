"""NOHRSC SNODAS Unmasked
"""

import os
import re
from datetime import datetime, timedelta

import pyplugs
from cumulus_geoproc import utils, logger
from cumulus_geoproc.snodas.core.process import process_snodas_for_date


this = os.path.basename(__file__)


@pyplugs.register
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
    outfile_list = []

    try:
        attr = {"GRIB_ELEMENT": "APCP"}

        filename = os.path.basename(src)
        filename_ = utils.file_extension(filename)

        # get date from filename like PRISM_ppt_early_4kmD2_yyyyMMdd_bil.zip
        time_pattern = re.compile(r"\w+_(?P<ymd>\d+)_\w+")

        m = time_pattern.match(filename)
        dt_valid = datetime.strptime(m.group("ymd"), "%Y%m%d")

    except (RuntimeError, KeyError, Exception) as ex:
        logger.error(f"{type(ex).__name__}: {this}: {ex}")
    finally:
        ds = None
        raster = None

    return outfile_list

    # # Fail fast if date can not be determined
    # dt = get_file_date()
    # if dt is None:
    #     return []

    # outfile_list = process_snodas_for_date(dt, infile, "UNMASKED", outdir)

    # return outfile_list
