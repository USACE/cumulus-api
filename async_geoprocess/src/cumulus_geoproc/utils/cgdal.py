"""_summary_
"""


def gdal_translate_options(**kwargs):
    base = {
        "format": "GTiff",
        "creationOptions": ["TILED=YES", "COPY_SRC_OVERVIEWS=YES", "COMPRESS=DEFLATE"],
    }
    return {**base, **kwargs}
