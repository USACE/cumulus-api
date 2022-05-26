"""High Resolution Rapid Refresh (HRRR) utilities


"""


import os
import re
from datetime import datetime, timezone

from cumulus_geoproc import logger

this = os.path.basename(__file__)


class HrrrIdx:
    """HRRR index (idx) files describe all elements in the grib2 file

    This class provides methods to parse lines from idx files and return a band
    number.  Logic to determine if the resulting parse values are done outside this
    class.
    """

    def __init__(self):
        self.el = None
        self.sep_ = ":"
        self.band = None
        self.cycle_dt = None
        self.desc = None
        self.fcst_hr = None
        self.sdf = "%Y%m%d%H%M"
        self.fcst_pattern = re.compile(r"\d+-?\d+")

    def __repr__(self):
        return f"{__class__.__name__}()"

    @property
    def element(self):
        return self.el

    def sep(self, s: str):
        self.sep = s

    def linex(self, line: str):
        try:
            parts = line.split(":")
            self.band = parts[0]
            self.cycle_dt = parts[2][2:]
            self.el = parts[3]
            self.desc = parts[4]
            self.fcst_hr = parts[5]
        except (ValueError, Exception) as ex:
            logger.error(f"{type(ex).__name__}: {this}: {ex}")

    @property
    def raster_band(self):
        try:
            return int(self.band)
        except:
            return

    @property
    def cycle_date(self):
        try:
            return datetime.strptime(self.cycle_date, self.sdf).replace(
                tzinfo=timezone.utc
            )
        except Exception as ex:
            logger.error(f"{type(ex).__name__}: {this}: {ex}")

    @property
    def description(self):
        return self.desc

    @property
    def forecast_hour(self):
        m = self.fcst_pattern.match(self.fcst_hr)
        if m:
            return eval(m[0])
        else:
            return -9999


if __name__ == "__main__":
    pass
