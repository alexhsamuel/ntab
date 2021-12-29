import numpy as np

from   tabela.index import Index
from   tabela.series import Series

#-------------------------------------------------------------------------------

def get_series():
    return Series(
        [  0,  -1, np.nan, 3.14159, 2.718, 100,   0,  1e-6],
        Index({
            "num"   : [  3,   6,      2,       1,     8,   2,    0,    6],
            "name"  : ["c", "c",    "d",     "f",   "q", "a", "d", "foo"],
        }),
        name="val"
    )


def test_repr():
    repr(get_series())


def test_str():
    str(get_series())


