"""_summary_
"""

import pyplugs


# @pyplugs
def writer(
    id: str,
    key: str,
    extent: dict,
    src: list[dict],
    dst: str,
    cellsize: float,
    srs_dst: str = "EPSG:5070",
    callback: function = None,
):
    # return None if no items in the 'contents'
    if len(src) < 1:
        return None


if __name__ == "__main__":
    pass
