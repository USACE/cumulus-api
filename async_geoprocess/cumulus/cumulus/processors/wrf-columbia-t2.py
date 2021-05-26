from ..wrfcolumbia.core import wrf2cog

def process(infile, outdir):
    """Takes an infile to process and path to a directory where output files should be saved
    Returns array of objects [{ "filetype": "nohrsc_snodas_swe", "file": "file.tif", ... }, {}, ]
    """

    varName = 'wrf-columbia-t2'
    outfile_list = wrf2cog(infile, outdir, varName)
    return outfile_list
    
