from   __future__ import absolute_import, division, print_function

import numpy as np
import pytest

from   ntab import Table, odict

#-------------------------------------------------------------------------------

def test_empty():
    tab = Table()
    with pytest.raises(RuntimeError):
        tab.length

    tab.a.x = np.arange(10)
    assert tab.length == 10
    tab.a.y = (np.arange(10) + 1)**2
    assert tab.length == 10
    
    assert tuple(tab.names) == ("x", "y")

    with pytest.raises(ValueError):
        tab.a.z = np.arange(12)

    assert tuple(tab.names) == ("x", "y")



def test_remove_last():
    tab = Table.from_cols({"x": [1, 3, 5, 7, 9]})
    assert tab.length == 5
    assert tuple(tab.names) == ("x", )

    del tab.a.x
    with pytest.raises(RuntimeError):
        tab.length
    assert tuple(tab.names) == ()


