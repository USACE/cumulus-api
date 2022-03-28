"""Prism Early
"""


from datetime import timezone
from ..prism.core import prism_datetime_from_filename
from ..prism.core import prism_convert_to_cog

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

    dt = prism_datetime_from_filename(infile)

    outfile_cog = prism_convert_to_cog(infile, outdir)

    outfile_list = [
        {
            "filetype": "prism-ppt-early",
            "file": outfile_cog,
            "datetime": dt.replace(tzinfo=timezone.utc).isoformat(),
            "version": None,
        },
    ]

    return outfile_list
