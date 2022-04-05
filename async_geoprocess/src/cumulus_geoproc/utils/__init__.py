"""utilities for the cumulus geoprocessor package
"""

import os
from signal import SIGINT, SIGTERM, signal


# ------------------------- #
# Signal Handler
# ------------------------- #
class SignalHandler:
    def __init__(self):
        self.received_signal = False
        signal(SIGINT, self._signal_handler)
        signal(SIGTERM, self._signal_handler)

    def _signal_handler(self, signal, frame):
        print(f"handling signal {signal}, exiting gracefully")
        self.received_signal = True


def file_extension(file: str, ext=".tif"):
    exts = (
        ".gz",
        ".tar",
        ".bin",
        ".grb",
        ".zip",
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


if __name__ == "__main__":
    print(file_extension("/path/to/file.grb", ext=""))
