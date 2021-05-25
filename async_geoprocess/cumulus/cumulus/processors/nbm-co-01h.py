from datetime import datetime
import os
from uuid import uuid4
from ..geoprocess.core.base import info, translate, create_overviews
from ..handyutils.core import change_final_file_extension
from dataclasses import dataclass, field
from typing import List, OrderedDict

@dataclass
class Band():
    band: int = 0
    block: List[int] = field(default_factory=lambda: [0,0])
    type: str = ""
    colorInterpretation: str = ""
    description: str = ""
    noDataValue: float = 0.0
    metadata: OrderedDict[str, OrderedDict[str,str]] = field(
        default_factory=lambda: {"", {"",""}}
        )

@dataclass
class Metadata():
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
class GribIds():
    CENTER: str = ""
    SUBCENTER: int = 0
    MASTER_TABLE: int = 0
    LOCAL_TABLE: int = 0
    SIGNF_REF_TIME: str = ""
    REF_TIME: datetime = datetime.now()
    PROD_STATUS: str = ""
    TYPE: str = ""


def process(infile, outdir):
    """Takes an infile to process and path to a directory where output files should be saved
    Returns array of objects [{ "filetype": "nohrsc_snodas_swe", "file": "file.tif", ... }, {}, ]
    """
    
    outfile_list = list()
    extract_bands = list()
    
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
        if ("Temperature" in meta.GRIB_COMMENT and "HTGL" in meta.GRIB_SHORT_NAME and \
            meta.GRIB_ELEMENT == "T" and meta.GRIB_UNIT == "[C]"):
            extract_bands.append({"filetype": "nbm-co-airtemp",
                                  "band_number": band_number,
                                  "ref_time": ref_time,
                                  "valid_time": valid_time})
        elif meta.GRIB_ELEMENT == "QPF01":
            extract_bands.append({"filetype": "nbm-co-qpf",
                                  "band_number": band_number,
                                  "ref_time": ref_time,
                                  "valid_time": valid_time})


    for e_band in extract_bands:
        # Extract Band; Convert to COG
        f_type = e_band["filetype"]
        b_number = e_band["band_number"]
        r_time = e_band["ref_time"]
        v_time = e_band["valid_time"]
        
        tif = translate(infile, os.path.join(outdir, f"temp-tif-{uuid4()}"), extra_args=["-b", str(b_number)])
        tif_with_overviews = create_overviews(tif)
        cog = translate(
            tif_with_overviews,
            os.path.join(
                outdir,
                change_final_file_extension(os.path.basename(infile), 'tif')            
            )
        )

        outfile_list.append({ "filetype": f_type, "file": cog, "datetime": v_time.isoformat(), "version": r_time })

    return outfile_list


