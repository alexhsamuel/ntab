from   __future__ import absolute_import, division, print_function

from   collections import OrderedDict as odict
import six

from   .tab import Table

#-------------------------------------------------------------------------------

def get_const(tab):
    """
    Finds cols in `tab` whose values are constant (same everywhere).

    A table with zero rows has no const cols.  A table with one row has all
    const cols.

    @return
      A mapping from col name to constant value, for cols whose arrays have
      the same value in every index.
    """
    const = odict()

    if tab.num_rows == 0:
        return const

    for name, arr in six.iteritems(tab.arrs):
        val = arr[0]
        if (arr == val).all():
            const[name] = val

    return const



def remove_const(tab):
    """
    Finds and removes const cols.

    @return
      As `get_const`.
    """
    const = get_const(tab)
    tab.remove(*const)
    return const


