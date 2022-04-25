"""_summary_
"""

from datetime import datetime, timezone


def swe():
    pass


def snow_depth():
    pass


def snow_temperature():
    pass


def snow_melt():
    pass


def cold_content():
    pass


def is_lakefix(dt: datetime, code: str):
    codes = ("1034", "1036")
    dt_after = datetime(2014, 10, 9, 0, 0, tzinfo=timezone.utc)
    if dt >= dt_after and code in codes:
        return True
    else:
        return False


if __name__ == "__main__":
    pass
