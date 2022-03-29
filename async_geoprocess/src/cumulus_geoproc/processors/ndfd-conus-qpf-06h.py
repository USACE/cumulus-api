"""NDFD CONUS QPF 6 hour
"""


from datetime import datetime, timezone
import os
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
    f_type = "ndfd-conus-qpf-06h"

    outfile_list = list()

    infilename = os.path.basename(infile)

    # Process the gdal information
    fileinfo: dict = info(infile)
    all_bands: List = fileinfo["bands"]

    # Get the band numbers for the products we want
    for bandx in all_bands:
        band_ = Band(**bandx)
        band_number = band_.band
        meta_dict = band_.metadata[""]
        meta = Metadata(**meta_dict)

        ref_time_str, _, ref_tz = meta.GRIB_REF_TIME.split()
        valid_time_str, _, valid_tz = meta.GRIB_VALID_TIME.split()
        ref_time = datetime.utcfromtimestamp(int(ref_time_str))
        valid_time = datetime.utcfromtimestamp(int(valid_time_str))

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
                "datetime": valid_time.replace(tzinfo=timezone.utc).isoformat(),
                "version": ref_time.replace(tzinfo=timezone.utc).isoformat(),
            }
        )

    return outfile_list
