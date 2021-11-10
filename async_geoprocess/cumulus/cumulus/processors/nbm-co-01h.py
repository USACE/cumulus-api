import os
import re
from collections import namedtuple
from uuid import uuid4
from datetime import datetime, timezone
from ..geoprocess.core.base import info, translate, create_overviews
from ..handyutils.core import change_final_file_extension

def process(infile, outdir):
    """Takes an infile to process and path to a directory where output files should be saved
    Returns array of objects [{ "filetype": "nohrsc_snodas_swe", "file": "file.tif", ... }, {}, ]
    
    National Blend of Models
    
    Band 46:
    --------
    01 hr Total precipitation [kg/(m^2)] at 0[-] SRC (Ground surface)
    
    Band 54: 
    --------
    Temperature [C] at 2[m] HTGL (Specified height above ground)
    
    """
    bands = {
        46: "nbm-co-airtemp",
        54: "nbm-co-qpf"
    }

    outfile_list = list()

    # Process the gdal information
    fileinfo: dict = info(infile)
    all_bands = fileinfo['bands']

    # Compile regex to get only the integer from times
    grib_time_pattern = re.compile(r'\d+')

    # Go through the bands dictionary to get the band and process the filetype
    for band, filetype in bands.items():
        band_ = all_bands[band]
        no_data_value = band_['noDataValue']
        metadata = band_['metadata']
        first_key = list(metadata.keys())[0]
        meta_grib = metadata[first_key]
        # Named tuple getting metadata
        Metadata = namedtuple(
            'Metadata',
            band_['metadata'][''].keys()
        )(**meta_grib)
        
        # Get the reference time and valid time
        # Assign empty string if no re.match()
        match_r_time = grib_time_pattern.search(Metadata.GRIB_REF_TIME)
        match_v_time = grib_time_pattern.search(Metadata.GRIB_VALID_TIME)
        # fromtimestamp with utc assignment gives proper iso format
        r_time = datetime.fromtimestamp(int(match_r_time[0]), timezone.utc) if match_r_time else ''
        v_time = datetime.fromtimestamp(int(match_v_time[0]), timezone.utc) if match_v_time else ''

        tif = translate(infile, os.path.join(outdir, f"temp-tif-{uuid4()}"), extra_args=["-b", str(band)])
        tif_with_overviews = create_overviews(tif)
        cog = translate(
            tif_with_overviews,
            os.path.join(
                outdir,
                change_final_file_extension(os.path.basename(infile), 'tif')
            )
        )

        outfile_list.append(
            {
                "filetype": filetype,
                "file": cog,
                "datetime": v_time.isoformat(),
                "version": r_time.isoformat()
            }
        )

    return outfile_list


