""" 
Unit test methods for cumulus-geoproc package
"""

import json
from pathlib import Path

from cumulus_geoproc.utils import cgdal

# gdal info from file
GDAL_INFO_HRRR = Path(__file__).parent.joinpath("gdal_info_hrrr.json").resolve()
GDAL_INFO_NBM = Path(__file__).parent.joinpath("gdal_info_nbmco.json").resolve()


def test_cgdal_find_hrrr_precip():
    """test_cgdal_find_hrrr_precip"""
    band = 90
    attr = {
        "GRIB_COMMENT": "01 hr Total precipitation [kg/(m^2)]",
        "GRIB_ELEMENT": "APCP01",
        "GRIB_UNIT": "[kg/(m^2)]",
    }

    with GDAL_INFO_HRRR.open("r", encoding="utf-8") as fptr:
        gdal_info = json.load(fptr)

    band_number = cgdal.band_from_json(gdal_info, attr, False)

    assert band_number == band, f"Band number {band_number} != {band}"


def test_cgdal_find_hrrr_precip_regex():
    """test_cgdal_find_hrrr_precip_regex"""
    band = 90
    attr = {
        "GRIB_COMMENT": "^01 hr Total precipitation \\[kg/\\(m\\^2\\)\\]",
        "GRIB_ELEMENT": "APCP01",
        "GRIB_UNIT": "\\[kg/\\(m\\^2\\)\\]",
    }

    with GDAL_INFO_HRRR.open("r", encoding="utf-8") as fptr:
        gdal_info = json.load(fptr)

    band_number = cgdal.band_from_json(gdal_info, attr, True)

    assert band_number == band, f"Band number {band_number} != {band}"


def test_cgdal_find_nbm_temperature():
    """test_cgdal_find_nbm_temperature"""
    band = 54
    attr = {
        "GRIB_COMMENT": "Temperature [C]",
        "GRIB_ELEMENT": "T",
        "GRIB_SHORT_NAME": "2-HTGL",
        "GRIB_UNIT": "[C]",
    }

    with GDAL_INFO_NBM.open("r", encoding="utf-8") as fptr:
        gdal_info = json.load(fptr)

    band_number = cgdal.band_from_json(gdal_info, attr, False)

    assert band_number == band, f"Band number {band_number} != {band}"


def test_cgdal_find_nbm_temperature_regex():
    """test_cgdal_find_nbm_temperature_regex"""
    band = 54
    attr = {
        "GRIB_COMMENT": "Temperature \\[C\\]",
        "GRIB_ELEMENT": "^T$",
        "GRIB_SHORT_NAME": "2\\-HTGL",
        "GRIB_UNIT": "\\[C\\]",
    }

    with GDAL_INFO_NBM.open("r", encoding="utf-8") as fptr:
        gdal_info = json.load(fptr)

    band_number = cgdal.band_from_json(gdal_info, attr, True)

    assert band_number == band, f"Band number {band_number} != {band}"


def test_cgdal_find_nbm_qpf():
    """test_cgdal_find_nbm_qpf"""
    band = 46
    attr = {"GRIB_ELEMENT": "QPF01", "GRIB_SHORT_NAME": "0-SFC"}

    with GDAL_INFO_NBM.open("r", encoding="utf-8") as fptr:
        gdal_info = json.load(fptr)

    band_number = cgdal.band_from_json(gdal_info, attr, False)

    assert band_number == band, f"Band number {band_number} != {band}"


def test_cgdal_find_nbm_qpf_regex():
    """test_cgdal_find_nbm_qpf_regex"""
    band = 46
    attr = {"GRIB_ELEMENT": "QPF01", "GRIB_SHORT_NAME": "0-SFC"}

    with GDAL_INFO_NBM.open("r", encoding="utf-8") as fptr:
        gdal_info = json.load(fptr)

    band_number = cgdal.band_from_json(gdal_info, attr, True)

    assert band_number == band, f"Band number {band_number} != {band}"
