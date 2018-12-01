import numpy as np

from   .lib import container
from   .tab import Table

#-------------------------------------------------------------------------------

def concat(*tabs):
    """
    Concatenates `tabs`.

    All must have the same names and dtypes, up to order.
    """
    dtypes = { n: a.dtype for n, a in tabs[0].arrs.items() }

    # First check dtypes.
    for tab in tabs[1 :]:
        tab_dtypes = { n: a.dtype for n, a in tab.arrs.items() }
        if tab_dtypes != dtypes:
            raise TypeError(f"dtypes do not match: {tab_dtypes}")

    # Collect and concatenate arrays.
    return Table(
        (n, np.concatenate([ t.arrs[n] for t in tabs ]))
        for n in dtypes
    )
        


def select_arrs(tab, names):
    """
    Returns a table with arrays selected by container `names`.
    """
    names = container.select_ordered(tab.names, names)
    return type(tab)( (n, tab.arrs[n]) for n in names )


def rename(tab, *args, **kw_args):
    """
    Renames arrays.

      >>> tab = Table(x=[3, 4, 5], y=[4, 5, 6])
      >>> rename(tab, axe="x", why="y")
      >>> sorted(tab.arrs.keys())
      ['axe', 'why']

    Arguments are converted to an ordered mapping from new to old array names,
    and applied in order.

    :raise KeyError:
      A given name was not found.
    """
    for new, old in dict(*args, **kw_args).items():
        tab.arrs[str(new)] = tab.arrs.pop(old)


def filter_mask(tab, **selections):
    """
    Constructs a mask from selections of array values.

      >>> tab = Table(x=[1, 2, 1, 2], y=[3, 4, 5, 6])
      >>> filter_mask(tab, x=2)
      array([False,  True, False,  True])

    :keywords:
      Names and values specifying specific values of arrays to select.
    :return:
      A boolean mask.
    """
    mask = None
    for name, value in selections.items():
        arr = tab.arrs[name]
        if mask is None:
            mask = arr == value
        else:
            mask[mask] &= arr[mask] == value
    return mask


def filter(tab, **selections):
    """
    Selects a subtable by selecting array values.

      >>> tab = Table(x=[1, 2, 1, 2], y=[3, 4, 5, 6])
      >>> print(filter(tab, x=2))
      x y
      - -
      2 4
      2 6
      <BLANKLINE>

    """
    return tab.rows[filter_mask(tab, **selections)]


def find(tab, **selections):
    """
    Selects a unique row by selecting array values.

      >>> tab = Table(x=[1, 2, 1, 2], y=[3, 4, 5, 6])
      >>> find(tab, y=5)
      Row(2, x=1, y=5)

    """
    idx = filter_mask(tab, **selections).nonzero()[0]
    if len(idx) == 0:
        raise LookupError("no item")
    elif len(idx) == 1:
        return tab.rows[idx[0]]
    else:
        raise LookupError("multiple items")


def get_const(tab):
    """
    Finds cols in `tab` whose values are constant (same everywhere).

    A table with zero rows has no const cols.  A table with one row has all
    const cols.

    :return:
      A mapping from col name to constant value, for cols whose arrays have
      the same value in every index.
    """
    const = dict()

    if tab.num_rows == 0:
        return const

    for name, arr in tab.arrs.items():
        val = arr[0]
        if (arr == val).all():
            const[name] = val

    return const


def remove_const(tab):
    """
    Finds and removes const cols.

    :return:
      As `get_const`.
    """
    const = get_const(tab)
    tab.remove(*const)
    return const


