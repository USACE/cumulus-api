"""Testing data array
"""
import ctypes

import numpy as np

tiffdss = ctypes.LibraryLoader(ctypes.CDLL).LoadLibrary("libtiffdss.so")

ND_POINTER_1 = np.ctypeslib.ndpointer(dtype=np.float32, ndim=1, flags="C")

# define prototypes
tiffdss.meanvalue.argtypes = [ND_POINTER_1, ctypes.c_int]
tiffdss.meanvalue.restype = ctypes.c_float

# create array X = [1 1 1 1 1]
X = np.arange(1000, 20000, dtype=np.float32)
# call function
ret = tiffdss.meanvalue(X, X.size)

print(f"{ret=}")
