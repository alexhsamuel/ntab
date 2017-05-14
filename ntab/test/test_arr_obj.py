from   __future__ import absolute_import, division, print_function

import numpy as np
import pytest

from   ntab import Table, odict

#-------------------------------------------------------------------------------

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


