from   __future__ import absolute_import, division, print_function

from   collections import OrderedDict as odict
import numpy as np
import pytest

from   ntab import Table

#-------------------------------------------------------------------------------

def test_rows():
    tab = Table([("x", [1, 2, 3, 4]), ("y", [2, 3, 4, 5]), ("z", [3, 4, 5, 16])])
    assert len(tab.rows) == 4
    assert list(tab.rows[ 0]) == [1, 2, 3]
    assert list(tab.rows[-1]) == [4, 5, 16]
    assert tab.rows[1].y == 3
    assert len(tab.rows[2]) == 3
    assert tab.rows[ 0].__idx__ == 0
    assert tab.rows[-1].__idx__ == 3
    assert dir(tab.rows[1]) == ["x", "y", "z"]


def test_row_str():
    tab = Table(odict(x=[1, 2, 3, 4], y=[2, 3, 4, 5], z=[3, 4, 5, 16]))
    s = str(tab.rows[1])
    assert "x" in s
    assert "y" in s
    assert "z" in s
    assert "w" not in s


def test_row_repr():
    tab = Table(odict(x=[1, 2, 3, 4], y=[2, 3, 4, 5], z=[3, 4, 5, 16]))
    r = repr(tab.rows[1])
    assert "x=2" in r
    assert "z=4" in r


