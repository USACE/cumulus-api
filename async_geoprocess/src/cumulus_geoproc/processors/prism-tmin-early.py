"""Prism tmin early
"""


from datetime import timezone
from ..prism.core import prism_datetime_from_filename
from ..prism.core import prism_convert_to_cog

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

    dt = prism_datetime_from_filename(infile)

    outfile_cog = prism_convert_to_cog(infile, outdir)

    outfile_list = [
        {
            "filetype": "prism-tmin-early",
            "file": outfile_cog,
            "datetime": dt.replace(tzinfo=timezone.utc).isoformat(),
            "version": None,
        },
    ]

    return outfile_list
