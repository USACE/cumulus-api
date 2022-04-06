"""utilities for the cumulus geoprocessor package
"""

import os
from zipfile import ZipFile


def file_extension(file: str, preffix: str = None, ext=".tif"):
    file = preffix + "-" + file if preffix else file

    exts = (
        ".gz",
        ".tar",
        ".bin",
        ".grb",
        ".zip",
        ".bil",
        ".grib",
        ".grib2",
        ".tar.gz",
        ".grib.gz",
        ".grib2.gz",
        ".grb.gz",
    )
    if file.endswith(exts):
        file_ = [
            file.replace(file[-len(e) :], ext) for e in exts if file[-len(e) :] == e
        ]

        return file_[-1]

    return file + ext


def uncompress(src: str, dst: str = "/tmp"):
    with ZipFile(src, "r") as zip_file:
        zip_file.extractall(path=dst)


if __name__ == "__main__":
    print(file_extension("/path/to/file.grb", ext=""))
