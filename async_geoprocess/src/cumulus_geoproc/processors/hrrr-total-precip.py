from datetime import datetime, timezone
import os
from uuid import uuid4
from cumulus_geoproc.geoprocess.core.base import info, translate, create_overviews
from cumulus_geoproc.handyutils.core import change_final_file_extension
from dataclasses import dataclass
from typing import List, OrderedDict
import pyplugs


@dataclass
class Band:
    band: int
    block: List[int]
    type: str
    colorInterpretation: str
    description: str
    metadata: OrderedDict[str, OrderedDict[str, str]]


@dataclass
class Metadata:
    GRIB_COMMENT: str
    GRIB_DISCIPLINE: str
    GRIB_ELEMENT: str
    GRIB_FORECAST_SECONDS: str
    GRIB_IDS: str
    GRIB_PDS_PDTN: str
    GRIB_PDS_TEMPLATE_ASSEMBLED_VALUES: str
    GRIB_PDS_TEMPLATE_NUMBERS: str
    GRIB_REF_TIME: str
    GRIB_SHORT_NAME: str
    GRIB_UNIT: str
    GRIB_VALID_TIME: str


@dataclass
class GribIds:
    CENTER: str
    SUBCENTER: int
    MASTER_TABLE: int
    LOCAL_TABLE: int
    SIGNF_REF_TIME: str
    REF_TIME: datetime
    PROD_STATUS: str
    TYPE: str


@pyplugs.register
def process(infile, outdir) -> List:
    """Takes an infile to process and path to a directory where output files should be saved
    Returns array of objects [{ "filetype": "nohrsc_snodas_swe", "file": "file.tif", ... }, {}, ]
    """
    band_number = 84
    outfile_list = list()

    # Process the gdal information
    fileinfo: dict = info(infile)
    all_bands: List = fileinfo["bands"]
    band84 = Band(**all_bands[band_number - 1])
    meta84_dict = band84.metadata[""]
    meta84 = Metadata(**meta84_dict)
    grib_ids_dict = dict(item.split("=") for item in meta84.GRIB_IDS.split(" "))
    grib_ids = GribIds(**grib_ids_dict)

    ref_time = datetime.fromisoformat(grib_ids.REF_TIME.replace("Z", "+00:00"))
    valid_time = datetime.fromtimestamp(int(meta84.GRIB_VALID_TIME.split(" ")[0]))

    # Extract Band; Convert to COG
    tif = translate(
        infile,
        os.path.join(outdir, f"temp-tif-{uuid4()}"),
        extra_args=["-b", str(band_number)],
    )
    tif_with_overviews = create_overviews(tif)
    cog = translate(
        tif_with_overviews,
        os.path.join(
            outdir, change_final_file_extension(os.path.basename(infile), "tif")
        ),
    )

    outfile_list.append(
        {
            "filetype": "hrrr-total-precip",
            "file": cog,
            "datetime": valid_time.replace(tzinfo=timezone.utc).isoformat(),
            "version": ref_time.replace(tzinfo=timezone.utc).isoformat(),
        }
    )

    return outfile_list
