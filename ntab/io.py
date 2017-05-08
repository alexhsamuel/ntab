from   __future__ import absolute_import, division, print_function, unicode_literals

from   builtins import *
import csv
import numpy as np

from   .tab import Table

#-------------------------------------------------------------------------------

CONVERT_DTYPES = [
    np.dtype("uint8"),
    np.dtype("int8"),
    np.dtype("uint16"),
    np.dtype("int16"),
    np.dtype("uint32"),
    np.dtype("int32"),
    np.dtype("uint64"),
    np.dtype("int64"),
    np.dtype("float32"),
    np.dtype("float64"),
]


def auto_convert(arr):
    for dtype in CONVERT_DTYPES:
        try:
            return arr.astype(dtype)
        except ValueError:
            continue
    else:
        return arr
    


def load(lines, names=None, **kw_args):
    reader = csv.reader(lines, **kw_args)
    names = tuple(next(reader) if names is None else ( str(n) for n in names ))
    arrs = [ auto_convert(np.array(a)) for a in zip(*reader) ]
    return Table(zip(names, arrs))

    

def read(path):
    with open(path, "rt") as file:
        return load(file)


