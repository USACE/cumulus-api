"""Testing with ctypes
"""
from ctypes import CDLL, LibraryLoader, c_char_p, c_int, c_longlong
import os
import cumulus_packager


# _cumulus_packager = os.path.dirname(cumulus_packager.__file__)
# libname = os.path.join(_cumulus_packager, "bin", "libtiffdss.so")
# so = CDLL(libname)
so = LibraryLoader(CDLL).LoadLibrary("libtiffdss.so")

write_record = so.writeRecord


write_record.argtypes = (
    c_longlong,
    c_char_p,
    c_char_p,
    c_char_p,
    c_char_p,
    c_char_p,
    c_char_p,
    c_char_p,
    c_char_p,
)
write_record.restype = c_int

src = c_char_p(b"/dss-test-data/tiff/MRMS_MultiSensor_QPE.tif")
dss = c_char_p(b"/dss-test-data/tiff/mydss.dss")
dsspath = c_char_p(b"/SHG/WATERSHED/PRECIP/07JUN2022:0900/07JUN2022:1000/MRMS/")
grid_type = c_char_p(b"shg-time")
dtype = c_char_p(b"per-cum")
unit = c_char_p(b"mm")
tz = c_char_p(b"gmt")
comp = c_char_p(b"zlib")


write_record(
    src,
    dss,
    dsspath,
    grid_type,
    dtype,
    unit,
    tz,
    comp,
)

print("Done")
