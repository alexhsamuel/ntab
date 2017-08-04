from   __future__ import absolute_import, division, print_function

import numpy as np
import pytest

from   ntab import Table

#-------------------------------------------------------------------------------

def make1():
    return Table([
        ("idx"      , [3, 4, 5, 6, 7]),
        ("const"    , [0, 0, 0, 0, 0]),
        ("val"      , [-1.0, 0.0, 4.0, 5.25, -3.125]),
        ("label"    , ["foo", "bar", "baz", "bif", "bum"]),
        ("check"    , [True, True, False, True, False]),
        ("exp"      , [0.1, 1, 10, 100, 1000]),
    ])


def test_empty():
    tab = Table()
    assert tab.num_cols == 0
    assert tab.num_rows == 0

    tab.a.x = np.arange(10)
    assert tab.num_cols == 1
    assert tab.num_rows == 10
    tab.a.y = (np.arange(10) + 1)**2
    assert tab.num_cols == 2
    assert tab.num_rows == 10
    
    assert tuple(tab.names) == ("x", "y")

    with pytest.raises(ValueError):
        tab.a.z = np.arange(12)

    assert tuple(tab.names) == ("x", "y")


def test_remove_last():
    tab = Table(x=[1, 3, 5, 7, 9])
    assert tab.num_cols == 1
    assert tab.num_rows == 5
    assert tuple(tab.names) == ("x", )

    del tab.a.x
    assert tab.num_cols == 0
    assert tab.num_rows == 0
    assert tuple(tab.names) == ()


def test_remove():
    tab = make1()
    assert list(tab.arrs) == ["idx", "const", "val", "label", "check", "exp"]
    tab.remove("val", "exp")
    assert list(tab.arrs) == ["idx", "const", "label", "check"]


