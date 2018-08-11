from   .lib import container

#-------------------------------------------------------------------------------

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
    


def get_const(tab):
    """
    Finds cols in `tab` whose values are constant (same everywhere).

    A table with zero rows has no const cols.  A table with one row has all
    const cols.

    @return
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

    @return
      As `get_const`.
    """
    const = get_const(tab)
    tab.remove(*const)
    return const


