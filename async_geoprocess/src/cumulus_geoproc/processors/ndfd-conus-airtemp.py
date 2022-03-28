"""NDFD CONUS Airtemp
"""


from datetime import datetime, timedelta, timezone
import os, sys
from pprint import pformat
from uuid import uuid4
from cumulus_geoproc.geoprocess.core.base import info, translate, create_overviews
from cumulus_geoproc.handyutils.core import change_final_file_extension
from dataclasses import dataclass, field
from typing import List, OrderedDict


@dataclass
class Band:
    band: int = 0
    block: List[int] = field(default_factory=lambda: [0, 0])
    type: str = ""
    colorInterpretation: str = ""
    description: str = ""
    noDataValue: float = 0.0
    metadata: OrderedDict[str, OrderedDict[str, str]] = field(
        default_factory=lambda: {"", {"", ""}}
    )


@dataclass
class Metadata:
    GRIB_COMMENT: str = ""
    GRIB_DISCIPLINE: str = ""
    GRIB_ELEMENT: str = ""
    GRIB_FORECAST_SECONDS: str = ""
    GRIB_IDS: str = ""
    GRIB_PDS_PDTN: str = ""
    GRIB_PDS_TEMPLATE_ASSEMBLED_VALUES: str = ""
    GRIB_PDS_TEMPLATE_NUMBERS: str = ""
    GRIB_REF_TIME: str = ""
    GRIB_SHORT_NAME: str = ""
    GRIB_UNIT: str = ""
    GRIB_VALID_TIME: str = ""


@dataclass
class GribIds:
    CENTER: str = ""
    SUBCENTER: int = 0
    MASTER_TABLE: int = 0
    LOCAL_TABLE: int = 0
    SIGNF_REF_TIME: str = ""
    REF_TIME: datetime = datetime.now()
    PROD_STATUS: str = ""
    TYPE: str = ""


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
    outfile_list = list()
    infilename = os.path.basename(infile)
    tdelta2 = timedelta()

    # Process the gdal information
    fileinfo: dict = info(infile)

    all_bands: List = fileinfo["bands"]

    # Build a list of dictionaries then run through that to translate the grid
    all_bands_list = list()
    for bandx in all_bands:
        tdelta1 = tdelta2
        band_ = Band(**bandx)
        band_number = band_.band
        meta_dict = band_.metadata[""]
        meta = Metadata(**meta_dict)

        ref_time = datetime.fromtimestamp(int(meta.GRIB_REF_TIME), timezone.utc)
        valid_time = datetime.fromtimestamp(int(meta.GRIB_VALID_TIME), timezone.utc)

        # Check the time deltas to see if they are consistant
        tdelta_seconds = float(meta.GRIB_FORECAST_SECONDS)
        tdelta2 = timedelta(seconds=tdelta_seconds)
        tdelta = (tdelta2 - tdelta1).seconds

        all_bands_list.append(
            {
                "band_number": band_number,
                "ref_time": ref_time,
                "valid_time": valid_time,
                "tdelta": tdelta,
            }
        )

    # Create a dictionary of time deltas and equivalent filetype
    f_type_dict = {
        3600: "ndfd-conus-airtemp-01h",
        10800: "ndfd-conus-airtemp-03h",
        21600: "ndfd-conus-airtemp-06h",
    }

    # First 36 hours are the same time delta for hourly and all the same for 6-hourly
    all_bands_list[0]["tdelta"] = all_bands_list[1]["tdelta"]

    # Create the tif files based on the list of dictionaries from above
    for i, band_list in enumerate(all_bands_list):
        try:
            f_type = f_type_dict[band_list["tdelta"]]
            valid_time = band_list["valid_time"]
            ref_time = band_list["ref_time"]
            tif = translate(
                infile,
                os.path.join(outdir, f"temp-tif-{uuid4()}"),
                extra_args=["-b", str(band_number)],
            )
            tif_with_overviews = create_overviews(tif)
            cog = translate(
                tif_with_overviews,
                os.path.join(
                    outdir, f"{infilename}-{valid_time.strftime('%Y%m%d%H%M')}.tif"
                ),
            )

            outfile_list.append(
                {
                    "filetype": f_type,
                    "file": cog,
                    "datetime": valid_time.isoformat(),
                    "version": ref_time.isoformat(),
                }
            )
        except KeyError as ex:
            print(ex)

    return outfile_list
