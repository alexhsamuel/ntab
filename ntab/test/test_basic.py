from   __future__ import absolute_import, division, print_function

import numpy as np
import pytest

from   ntab import Table

#-------------------------------------------------------------------------------

def test_init_dict():
    """
    Tests table initialization from a dict.
    """
    tab = Table(dict(x=[1, 2, 3], y=[2, 3, 4], z=[3, 4, 5]))
    assert tab.num_cols == 3
    assert tab.num_rows == 3
    assert sorted(tab.names) == ["x", "y", "z"]


def test_init_empty_dict():
    tab = Table(dict())
    assert tab.num_cols == 0
    assert tab.num_rows == 0
    assert tuple(tab.names) == ()


def test_init_odict():
    """
    Tests table initialization from an ordered dict.
    """
    arrs = dict()
    arrs["z"] = [3, 4, 5, 6]
    arrs["x"] = [1, 2, 3, 4]
    arrs["y"] = [2, 3, 4, 5]
    tab = Table(arrs)
    assert tab.num_cols == 3
    assert tab.num_rows == 4
    assert tuple(tab.arrs.keys()) == ("z", "x", "y")


def test_init_odict_empty():
    tab = Table(dict())
    assert tab.num_cols == 0
    assert tab.num_rows == 0
    assert tuple(tab.names) == ()


def test_init_kw_args():
    tab = Table(x=[4, 5, 6], z=[6, 7, 8], w=[2, 3, 4], y=[3, 4, 5])
    assert tab.num_cols == 4
    assert tab.num_rows == 3
    assert sorted(tab.names) == ["w", "x", "y", "z"]


def test_init_items():
    tab = Table([("x", [3, 4]), ("z", [1, 2]), ("y", [5, 6])])
    assert tab.num_cols == 3
    assert tab.num_rows == 2
    assert tuple(tab.names) == ("x", "z", "y")
    
    tab = Table([("x", [3, 4]), ("z", [1, 2]), ("y", [5, 6])], u=[8, 9])
    assert tab.num_cols == 4
    assert tab.num_rows == 2
    assert tuple(tab.names) == ("x", "z", "y", "u")
    

def test_init_bad_length():
    with pytest.raises(ValueError):
        Table(dict(x=[1, 2, 3], y=[1, 2]))
    with pytest.raises(ValueError):
        Table(x=[3], y=[4], z=[5], u=[], w=[2])
    with pytest.raises(ValueError):
        Table([("x", [3, 4, 5, 6]), ("y", [4, 5, 6, 7]), ("z", [2, 3, 4])])
    with pytest.raises(ValueError):
        Table([("x", [3, 4, 5, 6]), ("y", [4, 5, 6, 7])], z=[2, 3, 4])


def test_empty_arrs():
    tab = Table(x=[], y=[], z=[])
    assert tab.num_cols == 3
    assert tab.num_rows == 0


def test_tab_create_scalar():
    tab = Table(i=2, x=[3, 4, 5], l="foo")
    assert tab.num_rows == 3
    assert list(tab.a.i) == [2, 2, 2]
    assert list(tab.a.l) == ["foo", "foo", "foo"]


def test_tab_add_col_scalar():
    tab = Table(x=[3, 4, 5])
    tab.a.i = 2
    tab.a.l = "foo"
    assert list(tab.a.i) == [2, 2, 2]
    assert list(tab.a.l) == ["foo", "foo", "foo"]


