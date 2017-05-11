from   __future__ import absolute_import, division, print_function

import numpy as np
import pytest

from   ntab import Table, odict

#-------------------------------------------------------------------------------

def test_basic0():
    tab = Table.from_cols((("x", [1, 3, 5, 7, 9]), ("y", [2, 4, 6, 8, 0])))
    assert tab.length == 5
    assert tuple(tab.arrs.keys()) == ("x", "y")


def test_empty():
    tab = Table()
    with pytest.raises(RuntimeError):
        tab.length
    tab.a.x = np.arange(10)
    assert tab.length == 10
    tab.a.y = (np.arange(10) + 1)**2
    assert tab.length == 10
    
    with pytest.raises(ValueError):
        tab.a.z = np.arange(12)


