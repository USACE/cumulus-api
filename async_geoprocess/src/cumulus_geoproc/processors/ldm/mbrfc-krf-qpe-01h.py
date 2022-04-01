"""Missouri Basin River Forecast Center
"""


import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, OrderedDict
from uuid import uuid4

from cumulus_geoproc.geoprocess.core.base import create_overviews, info, translate, warp
from cumulus_geoproc.handyutils.core import change_final_file_extension, gunzip_file
import pyplugs


@dataclass
class Band:
    band: int
    block: List[int]
    type: str
    colorInterpretation: str
    description: str
    noDataValue: float
    metadata: OrderedDict[str, OrderedDict[str, str]]


@dataclass
class Metadata:
    GRIB_COMMENT: str
    # GRIB_DISCIPLINE: str
    GRIB_ELEMENT: str
    GRIB_FORECAST_SECONDS: str
    # GRIB_IDS: str
    # GRIB_PDS_PDTN: str
    # GRIB_PDS_TEMPLATE_ASSEMBLED_VALUES: str
    # GRIB_PDS_TEMPLATE_NUMBERS: str
    GRIB_REF_TIME: str
    GRIB_SHORT_NAME: str
    GRIB_UNIT: str
    GRIB_VALID_TIME: str


# @dataclass
# class GribIds():
#     CENTER: str
#     SUBCENTER: int
#     MASTER_TABLE: int
#     LOCAL_TABLE: int
#     SIGNF_REF_TIME: str
#     REF_TIME: datetime
#     PROD_STATUS: str
#     TYPE: str


# @pyplugs.register
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
    band_number = 1
    ftype = "mbrfc-krf-qpe-01h"

    outfile_list = list()

    # Process the gdal information
    new_infile = os.path.splitext(infile)[0]
    gunzip_file(infile, new_infile)
    fileinfo: dict = info(new_infile)

    all_bands: List = fileinfo["bands"]
    band = Band(**all_bands[band_number - 1])
    meta_dict = band.metadata[""]
    meta = Metadata(**meta_dict)

    # ref_time = datetime.fromtimestamp(int(meta.GRIB_REF_TIME))
    valid_time = datetime.fromtimestamp(int(meta.GRIB_VALID_TIME), timezone.utc)

    # Extract Band; Convert to COG

    tif_trans = translate(
        new_infile,
        os.path.join(outdir, f"temp-tif-{uuid4()}"),
        extra_args=["-b", str(band_number)],
    )
    tif_with_overviews = create_overviews(tif_trans)
    cog = translate(
        tif_with_overviews,
        os.path.join(
            outdir, change_final_file_extension(os.path.basename(new_infile), "tif")
        ),
    )

    outfile_list.append(
        {
            "filetype": ftype,
            "file": cog,
            "datetime": valid_time.isoformat(),
            "version": None,
        }
    )

    return outfile_list
