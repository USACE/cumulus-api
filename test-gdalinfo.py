from datetime import datetime
from dataclasses import dataclass
from typing import List, OrderedDict
import json

@dataclass
class Band():
    band: int
    block: List[int]
    type: str
    colorInterpretation: str
    description: str
    metadata: OrderedDict[str, OrderedDict[str,str]]

@dataclass
class Metadata():
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
class GribIds():
    CENTER: str
    SUBCENTER: int
    MASTER_TABLE: int
    LOCAL_TABLE: int
    SIGNF_REF_TIME: str
    REF_TIME: datetime
    PROD_STATUS: str
    TYPE: str

with open("/Users/rdcrljsg/projects/cumulus-api/tmp/fileinfo", "r") as f:
    data = json.loads(f.read())

all_bands: List = data["bands"]

band84 = Band(**all_bands[83])

meta84_dict = band84.metadata[""]
meta84 = Metadata(**meta84_dict)
grib_ids_dict = dict(item.split("=") for item in meta84.GRIB_IDS.split(" "))
grib_ids = GribIds(**grib_ids_dict)

dt = datetime.fromisoformat(grib_ids.REF_TIME.replace("Z", "+00:00"))

print(dt)

dt = datetime.fromtimestamp(int(meta84.GRIB_VALID_TIME.split(" ")[0]))

print(dt)