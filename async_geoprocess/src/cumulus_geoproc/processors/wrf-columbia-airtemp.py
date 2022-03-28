"""WRF Columbia Airtemp
"""

from cumulus_geoproc.wrfcolumbia.core import wrf2cog

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

    varName = "wrf-columbia-airtemp"
    outfile_list = wrf2cog(infile, outdir, varName)
    return outfile_list
