"""Geoprocessing SNODAS state variables
"""


import re
from datetime import datetime, timezone

BOUNDING_DATE: datetime = datetime.fromisoformat("2013-10-01").replace(
    tzinfo=timezone.utc
)

translate_options: dict = {
    "global": {
        "format": "GTiff",
        "outputSRS": "+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs",
        "noData": -9999,
    },
    "masked": {
        "hdr": "ENVI\nsamples = 6935\nlines = 3351\nbands = 1\nheader offset = 0\nfile type = ENVI Standard\ndata type = 2\ninterleave = bsq\nbyte order = 1\n",
        "translate_option": {
            0: {  # >= 2013-10-01 => False
                "outputBounds": [
                    -124.73375000000000,
                    52.87458333333333,
                    -66.94208333333333,
                    24.94958333333333,
                ],
            },
            1: {  # >= 2013-10-01 => True
                "outputBounds": [
                    -124.73333333333333,
                    52.87500000000000,
                    -66.94166666666667,
                    24.95000000000000,
                ],
            },
        },
    },
    "unmasked": {
        "hdr": "ENVI\nsamples = 8192\nlines = 4096\nbands = 1\nheader offset = 0\nfile type = ENVI Standard\ndata type = 2\ninterleave = bsq\nbyte order = 1\n",
        "translate_option": {
            0: {  # > 2013-10-01 => False
                "outputBounds": [
                    -130.51708333333333,
                    58.23291666666667,
                    -62.25041666666667,
                    24.09958333333333,
                ],
            },
            1: {  # >= 2013-10-01 => True
                "outputBounds": [
                    -130.51666666666667,
                    58.23333333333333,
                    -62.25000000000000,
                    24.10000000000000,
                ],
            },
        },
    },
}


regions: dict = {"us": "masked", "zz": "unmasked"}
product_code: dict = {
    1025: {"description": "Precipitation", "product": None},
    1034: {"description": "Snow water equivalent", "product": "nohrsc-snodas-swe"},
    1036: {"description": "Snow depth", "product": "nohrsc-snodas-snowdepth"},
    1038: {
        "description": "Snow pack average temperature",
        "product": "nohrsc-snodas-snowpack-average-temperature",
    },
    1039: {"description": "Blowing snow sublimation", "product": None},
    1044: {"description": "Snow melt", "product": "nohrsc-snodas-snowmelt"},
    1050: {"description": "Snow pack sublimation", "product": None},
    2072: {"description": "", "product": "nohrsc-snodas-coldcontent"},
    3333: {"description": "Snow melt (mm)", "product": "nohrsc-snodas-snowmelt"},
}

snow_integration: dict = {
    "lL00": "Fluxes to and from the snow surface such as sublimation",
    "tS__": "Integral through all the layers of the snow pack",
    "bS__": "Bottom of the snow pack such as snow melt",
    "wS__": "Snow-water-equivalent-weighted average of the snowpack layers",
}

precip_integration: dict = {
    "lL00": "Non-snow (liquid) precipitation",
    "lL01": "Snow precipitation",
}


class SnodasFilenameParse:
    """Class to parse SNODAS filename

    pattern = "rr_mmmffppppSvvvvTttttaaaaTSyyyymmddhhIP00Z.xxx.ee"
    """

    def __init__(self, filename):
        self.filename = filename

    @property
    def region(self):
        region_ = self.filename[:2]
        if region_ == "us":
            return "masked"
        elif region_ == "zz":
            return "unmasked"
        else:
            return "unknown"

    @property
    def model(self):
        return self.filename[3:6]

    @property
    def version(self):
        return self.filename[6:8]

    @property
    def product(self):
        return self.filename[8:12]

    @property
    def vertical_integration(self):
        m = re.match(r"\w{7}\d{5}S*([lL|tS|bS|wS]\w{3}).*", self.filename)
        return m[1]

    @property
    def time_integration(self):
        m = re.match(r".*([AT]\d{4}).*", self.filename)
        return m[1]

    @property
    def model_operations(self):
        return "TTNA"

    @property
    def time_step(self):
        m = re.match(r".*TS(\d{10}).*", self.filename)
        return m[1]

    @property
    def date_time(self):
        return datetime.strptime(self.time_step(), "%Y%m%d%H").replace(
            tzinfo=timezone.utc
        )

    @property
    def offset(self):
        m = re.match(r".*TS(\d{10}).*", self.filename)
        return m[1]

    @property
    def extension(self):
        m = re.match(r".*(\.\w{3}).*", self.filename)
        return m[1]


if __name__ == "__main__":
    parse = SnodasFilenameParse("zz_ssmv01025SlL01T0024TTNATS2010041905DP001.dat")
    print(parse.offset)
    parse = SnodasFilenameParse("zz_ssmv11038wS__A0024TTNATS2010041905DP001.dat")
    print(parse.offset)
