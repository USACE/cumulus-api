"""NOHRSC SNODAS Unmasked
"""

import os
import re
from datetime import datetime, timedelta

import pyplugs
from cumulus_geoproc.snodas.core.process import process_snodas_for_date


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

    def get_file_date():
        """Helper function to strip date from the filename"""
        m = re.match(r"SNODAS_unmasked_([0-9]+).tar", os.path.basename(infile))

        if m is not None:
            return datetime.strptime(m[1], "%Y%m%d") + timedelta(hours=6)

        return None

    # Fail fast if date can not be determined
    dt = get_file_date()
    if dt is None:
        return []

    outfile_list = process_snodas_for_date(dt, infile, "UNMASKED", outdir)

    return outfile_list
