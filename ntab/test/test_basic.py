from   __future__ import absolute_import, division, print_function

import numpy as np
import pytest

from   ntab import Table, odict

#-------------------------------------------------------------------------------

def test_basic0():
    tab = Table.from_arrs((("x", [1, 3, 5, 7, 9]), ("y", [2, 4, 6, 8, 0])))
    assert tab.num_cols == 2
    assert tab.num_rows == 5
    assert tuple(tab.arrs.keys()) == ("x", "y")


