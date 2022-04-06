"""WRF Columbia Airtemp
"""

from cumulus_geoproc.wrfcolumbia.core import wrf2cog

import pyplugs


this = os.path.basename(__file__)
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

    varName = "wrf-columbia-airtemp"
    outfile_list = wrf2cog(infile, outdir, varName)
    return outfile_list
