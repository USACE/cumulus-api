"""SNODAS interpolate

example message for this process:

    {
        'geoprocess': 'snodas-interpolate',
        'geoprocess_config': {
            'bucket': 'castle-data-develop',
            'datetime': '20220323',
            'max_distance': 16
        }
    }

"""

import os

from cumulus_geoproc.utils import cgdal
from cumulus_geoproc.snodas import product_code as snodas_product_code

this = os.path.basename(__file__)


def cold_content(translated_tif):
    """
    {
        "file": tif,
        "filetype": snodas_product_code[snodas_file.product]["product"],
        "datetime": snodas_file.date_time.isoformat(),
        "version": None,
    }
    """
    swe = translated_tif[1034]["file"]
    dt = translated_tif[1034]["datetime"]
    avg_temp = translated_tif[1038]["file"]

    cold_content_filename = swe.replace("1034", "2072")
    cgdal.gdal_calculate(
        "-A",
        swe,
        "-B",
        avg_temp,
        "--outfile",
        tif := cold_content_filename,
        "--calc",
        "A.astype(numpy.float64) * 2114 * (B.astype(numpy.float64) - 273) / 333000",
    )

    return {
        "file": tif,
        "filetype": snodas_product_code[2072]["product"],
        "datetime": dt,
        "version": None,
    }
