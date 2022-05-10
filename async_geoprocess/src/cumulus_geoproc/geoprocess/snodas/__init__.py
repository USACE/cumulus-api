"""Geoprocessing SNODAS state variables

Reference:
    https://nsidc.org/sites/nsidc.org/files/G02158-V001-UserGuide_2.pdf
"""


import os
from datetime import datetime, timezone
from string import Template

from cumulus_geoproc import logger
from cumulus_geoproc.utils import cgdal
from osgeo import gdal

gdal.UseExceptions()

this = os.path.basename(__file__)


product_code: dict = {
    "1025": {
        "description": "Precipitation",
        "product": None,
        "file_template": None,
    },
    "1034": {
        "description": "Snow water equivalent",
        "product": "nohrsc-snodas-swe",
        "file_template": Template("zz_ssmv11034tS__T0001TTNATS${YMD}05HP001.tif"),
    },
    "1036": {
        "description": "Snow depth",
        "product": "nohrsc-snodas-snowdepth",
        "file_template": Template("zz_ssmv11036tS__T0001TTNATS${YMD}05HP001.tif"),
    },
    "1038": {
        "description": "Snow pack average temperature",
        "product": "nohrsc-snodas-snowpack-average-temperature",
        "file_template": Template("zz_ssmv11038wS__A0024TTNATS${YMD}05DP001.tif"),
    },
    "1039": {
        "description": "Blowing snow sublimation",
        "product": None,
        "file_template": None,
    },
    "1044": {
        "description": "Snow melt",
        "product": "nohrsc-snodas-snowmelt",
        "file_template": Template("zz_ssmv11044bS__T0024TTNATS${YMD}05DP000.tif"),
    },
    "1050": {
        "description": "Snow pack sublimation",
        "product": None,
        "file_template": None,
    },
    "2072": {
        "description": "",
        "product": "nohrsc-snodas-coldcontent",
        "file_template": Template("zz_ssmv12072tS__T0001TTNATS${YMD}05HP001.tif"),
    },
    "3333": {
        "description": "Snow melt (mm)",
        "product": "nohrsc-snodas-snowmelt",
        "file_template": Template("zz_ssmv13333bS__T0024TTNATS${YMD}05DP000.tif"),
    },
}


def no_data_value(dt: datetime):
    """No data value determined by time

    Parameters
    ----------
    dt : datetime
        datetime object

    Returns
    -------
    int
        raster no data value
    """
    dt_nodata = datetime(2011, 1, 24, 0, 0, tzinfo=timezone.utc)
    if dt < dt_nodata:
        return "55537"
    else:
        return "-9999"


def snow_melt_mm(translated_tif: dict):
    """Dictionary of tiffs generated from gdal translate

    Parameters
    ----------
    translated_tif : dict

        "product_code": {
            "filetype": str,         Matching database acquirable
            "file": str,             Converted file
            "datetime": str,         Valid Time, ISO format with timezone
            "version": str           Reference Time (forecast), ISO format with timezone
        }

    Returns
    -------
    dict
        {
            "filetype": str,         Matching database acquirable
            "file": str,             Converted file
            "datetime": str,         Valid Time, ISO format with timezone
            "version": str           Reference Time (forecast), ISO format with timezone
        }
    """
    snowmelt_code = "1044"
    snowmelt_code_mm = "3333"

    snowmelt = translated_tif[snowmelt_code]["file"]
    snowmelt_dt = translated_tif[snowmelt_code]["datetime"]

    snowmelt_mm = snowmelt.replace(snowmelt_code, snowmelt_code_mm)
    temp_snowmelt_mm = snowmelt.replace(snowmelt_code, "9999")

    # convert snow melt runoff as meters / 100_000 to mm
    # 100_000 is the scale factor getting values to meters
    try:
        cgdal.gdal_calculate(
            "-A",
            snowmelt,
            "--outfile",
            temp_snowmelt_mm,
            "--calc",
            "A.astype(numpy.float32) / 100_000 * 1000",
            "--quiet",
            "--overwrite",
        )
        gdal.Translate(
            tif := snowmelt_mm,
            temp_snowmelt_mm,
            format="COG",
            creationOptions=[
                "RESAMPLING=AVERAGE",
                "OVERVIEWS=IGNORE_EXISTING",
                "OVERVIEW_RESAMPLING=AVERAGE",
            ],
        )
        # validate COG
        if (validate := cgdal.validate_cog("-q", tif)) == 0:
            logger.info(f"Validate COG = {validate}\t{tif} is a COG")
    except RuntimeError as ex:
        logger.debug(f"{type(ex).__name__}: {this}: {ex}")
        return None

    return {
        snowmelt_code_mm: {
            "file": tif,
            "filetype": product_code[snowmelt_code_mm]["product"],
            "datetime": snowmelt_dt,
            "version": None,
        }
    }


def cold_content(translated_tif):
    """Compute cold content as a function of SWE and snow pack avg temp

    Parameters
    ----------
    translated_tif : dict

        "product_code": {
            "filetype": str,         Matching database acquirable
            "file": str,             Converted file
            "datetime": str,         Valid Time, ISO format with timezone
            "version": str           Reference Time (forecast), ISO format with timezone
        }

    Returns
    -------
    dict
        {
            "filetype": str,         Matching database acquirable
            "file": str,             Converted file
            "datetime": str,         Valid Time, ISO format with timezone
            "version": str           Reference Time (forecast), ISO format with timezone
        }
    """
    coldcontent_code = "2072"
    swe_code = "1034"
    avg_temp_sp = "1038"

    swe = translated_tif[swe_code]["file"]
    swe_dt = translated_tif[swe_code]["datetime"]
    avg_temp = translated_tif[avg_temp_sp]["file"]

    cold_content_filename = swe.replace(swe_code, coldcontent_code)
    temp_cold_content = swe.replace(swe_code, "9999")

    try:
        cgdal.gdal_calculate(
            "-A",
            swe,
            "-B",
            avg_temp,
            "--outfile",
            temp_cold_content,
            "--calc",
            "A.astype(numpy.float32) * 2114 * (B.astype(numpy.float32) - 273) / 333000",
            "--quiet",
        )
        gdal.Translate(
            tif := cold_content_filename,
            temp_cold_content,
            format="COG",
            creationOptions=[
                "RESAMPLING=AVERAGE",
                "OVERVIEWS=IGNORE_EXISTING",
                "OVERVIEW_RESAMPLING=AVERAGE",
            ],
        )
        # validate COG
        if (validate := cgdal.validate_cog("-q", tif)) == 0:
            logger.info(f"Validate COG = {validate}\t{tif} is a COG")
    except RuntimeError as ex:
        logger.debug(f"{type(ex).__name__}: {this}: {ex}")
        return None

    return {
        coldcontent_code: {
            "file": tif,
            "filetype": product_code[coldcontent_code]["product"],
            "datetime": swe_dt,
            "version": None,
        }
    }


if __name__ == "__main__":
    pass
