from datetime import datetime, timezone

import os
from uuid import uuid4
from ..geoprocess.core.base import info, translate, create_overviews
from ..handyutils.core import change_final_file_extension, gunzip_file
from dataclasses import dataclass
from typing import List, OrderedDict


@dataclass
class Band:
    band: int
    block: List[int]
    type: str
    colorInterpretation: str
    description: str
    # noDataValue: float
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

import pyplugs


@pyplugs.register
def process(infile, outdir) -> List:
    """Takes an infile to process and path to a directory where output files should be saved
    Returns array of objects [{ "filetype": "nohrsc_snodas_swe", "file": "file.tif", ... }, {}, ]
    """
    band_number = 1
    ftype = "serfc-qpf-06h"

    outfile_list = list()

    # Process the gdal information
    new_infile = os.path.splitext(infile)[0]
    gunzip_file(infile, new_infile)
    fileinfo: dict = info(new_infile)

    all_bands: List = fileinfo["bands"]
    band = Band(**all_bands[band_number - 1])
    meta_dict = band.metadata[""]
    meta = Metadata(**meta_dict)

    ref_time = datetime.fromtimestamp(int(meta.GRIB_REF_TIME.split(" ")[0]))
    valid_time = datetime.fromtimestamp(int(meta.GRIB_VALID_TIME.split(" ")[0]))

    # Extract Band; Convert to COG
    tif = translate(
        new_infile,
        os.path.join(outdir, f"temp-tif-{uuid4()}"),
        extra_args=["-b", str(band_number)],
    )
    tif_with_overviews = create_overviews(tif)
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
            "datetime": valid_time.replace(tzinfo=timezone.utc).isoformat(),
            "version": ref_time.replace(tzinfo=timezone.utc).isoformat(),
        }
    )

    return outfile_list
