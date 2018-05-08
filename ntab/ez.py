"""
Convenience functions, many of questionable taste.

If you're the sort to be offended easily by obscure and opaque hackery, please
cover your eyes and don't use this module.
"""

#-------------------------------------------------------------------------------

from   __future__ import absolute_import, division, print_function, unicode_literals

from   contextlib import contextmanager
import numpy as np
import sys

from   .tab import Table

#-------------------------------------------------------------------------------

@contextmanager
def vars(tab, add_cols=True):
    """
    Context manager with columns as variables.

    Stuffs column arrays as global variables into the the calling context.
    (New local variables inserted into a function's locals don't work in 
    Python.)  

      >>> tab = Table(x=[3, 4, 5], y=[4, 5, 6])
      >>> with vars(tab):
      ...     print(x.sum(), y.sum())
      12 15

    If `add_cols` is true, any new local variables created whose values are
    one-dimensional numpy arrays of the right length are added to the table
    as new columns.

      >>> with vars(tab):
      ...     s = x + y
      ...     d = y - x
      >>> print(tab.a.s)
      [ 7  9 11]
      >>> print(tab.a.d)
      [1 1 1]

    """
    globals     = sys._getframe(2).f_globals
    old_locals  = sys._getframe(2).f_locals.copy()

    # FIXME: Sanitize names?
    globals.update(tab.arrs)

    # Run the context.
    try:
        yield

    finally:
        # Take the arrs back out of the namespace.
        for name, arr in tab.arrs.items():
            try:
                val = globals[name]
            except KeyError:
                # Must have been deleted.
                pass
            else:
                if val is arr:
                    # Clean it up.
                    del globals[name]

        if add_cols:
            # Look for new local array variables of the right length, and add
            # them in.
            for name, val in sys._getframe(2).f_locals.items():
                if (old_locals.get(name, None) is not val
                    and isinstance(val, np.ndarray) 
                    and val.shape == (tab.num_rows, )
                ):
                    tab.arrs[name] = val



