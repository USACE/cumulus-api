"""_summary_
"""

from ctypes import CDLL, LibraryLoader, c_char_p, c_float, c_int, c_longlong

tiffdss = LibraryLoader(CDLL).LoadLibrary("libtiffdss.so")
zopen = tiffdss.opendss
zopen.argtypes = [c_longlong, c_char_p]
zopen.restype = c_int
zclose = tiffdss.closedss
zclose.argtypes = [c_longlong]
zclose.restype = c_int
write_record = tiffdss.writeRecord
write_record.argtypes = [
    c_longlong,
    c_float,
    c_char_p,
    c_char_p,
    c_char_p,
    c_char_p,
    c_char_p,
    c_char_p,
    c_char_p,
]
write_record.restype = c_int
