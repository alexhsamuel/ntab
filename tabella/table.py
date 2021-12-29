import collections.abc
import numpy as np
import re

from   . import fmt
from   .column import Column
from   .lib import container, memo, py, text

NO_DEFAULT = object()

#-------------------------------------------------------------------------------

class Row(collections.abc.Mapping):
    """
    A (virtual) row in a table or relation.
    """

    __slots__ = ("__idx", "__arrs")

    def __init__(self, idx, arrs):
        self.__idx = idx
        self.__arrs = arrs


    def __repr__(self):
        i = self.__idx
        items = ( f"{n}={a[i]!r}" for n, a in self.__arrs.items() )
        return f"Row({', '.join(items)})"


    def __str__(self):
        return "\n".join(fmt.format_row(self))


    def _repr_html_(self):
        from . import html
        return html.format_exc(html.render_row)(self)


    @property
    def __idx__(self):
        return self.__idx


    # Mapping

    def __len__(self):
        return len(self.__arrs)


    def __iter__(self):
        return iter(self.__arrs)


    def keys(self):
        return self.__arrs.keys()


    def values(self):
        idx = self.__idx
        return ( a[idx] for a in self.__arrs.values() )


    def items(self):
        idx = self.__idx
        return ( (n, a[idx]) for n, a in self.__arrs.items() )


    def __getitem__(self, name):
        # FIXME: Slicing.
        return self.__arrs[name][self.__idx]



#-------------------------------------------------------------------------------

class Table:
    """
    Data table consisting of named parallel `ndarray`s.

    A table consists of zero or more cols, representing columns, each of which
    must be one-dimensional and of the same length.  The column cols are taken
    to be parallel: each "row" of the tabel consists of corresponding elements
    of the column cols.
    """

    def __init__(self, cols):
        """
        Constructs a new table from named parallel arrays.

        Columns are converted to `ndarray`, if necessary.  They must all be
        one-dimensional and the same length.
        """
        self.__cols = { str(n): Column.wrap(c) for n, c in cols.items() }
        try:
            self.__length = py.all_equal(
                ( len(c.arr) for c in self.__cols.values() ),
                default=0
            )
        except ValueError:
            raise ValueError("not the same length") from None


    def __repr__(self):
        return py.format_ctor(
            self,
            {
                # Remove newlines from NumPy's reprs.
                n: re.sub(r"\s+", " ", repr(c.arr))
                for n, c in self.__cols.items()
            }
        )


    # Max number of rows to show in __str__.
    # FIXME: Get rid of this foolery.
    STR_MAX_ROWS = 16

    def __str__(self):
        return text.join_lines(fmt.format_arrs(
            ( (n, c.arr) for n, c in self.__cols.items() ),
            max_length=self.STR_MAX_ROWS
        ))


    def __reduce__(self):
        return self.__class__, (self.__cols, )


    #---------------------------------------------------------------------------

    @memo.lazy_property
    def _arrs(self):
        return { n: c.arr for n, c in self.__cols.items() }


    def _take_rows(self, idxs):
        return self.__class__(
            # FIXME: a.take(idxs) _should_ be faster, but its 1000x slower if
            # a is not a contiguous array.
            (n, a[idxs]) for n, a in self.__arrs.items()
        )


    def __get_subtable(self, sel):
        # FIXME: Store the mask in the table and filter lazily.
        return self.__class__(
            { n: c.arr[sel] for n, c in self.__cols.items() })


    def _select_cols(self, names):
        return self.__class__({n: self.__cols[n] for n in names })


    #---------------------------------------------------------------------------
    # Table.cols proxy object

    class Cols(collections.abc.MutableMapping):
        """
        A mapping from name to arr.
        """

        def __init__(self, table):
            self.__table = table
            self.__cols = table._Table__cols


        def __repr__(self):
            return "Table.Cols"


        # MutableMapping -------------------------------------------------------

        def __len__(self):
            return len(self.__cols)


        def __iter__(self):
            return iter(self.__cols)


        def keys(self):
            return self.__cols.keys()


        def values(self):
            return ( c.arr for c in self.__cols.values() )


        def items(self):
            return ( (n, c.arr) for n, c in self.__cols.items() )


        def get(self, key, /, default=NO_DEFAULT) -> np.ndarray:
            """
            Retrieves a col by name or index.

            :param key:
              A str col name, or int col idx.
            """
            if not isinstance(key, str):
                # Try as int idx.
                try:
                    idx = int(key)
                except (TypeError, ValueError):
                    # Not an integer.  Fall through.
                    pass
                else:
                    # Look up by int idx.
                    try:
                        return tuple(self.__cols.values())[idx].arr
                    except IndexError:
                        if default is NO_DEFAULT:
                            raise KeyError(idx) from None
                        else:
                            return default
            # Try as str name.
            try:
                return self.__cols[str(key)].arr
            except KeyError:
                if default is NO_DEFAULT:
                    raise
                else:
                    return default


        __getitem__ = get


        def __setitem__(self, name, arr):
            # FIXME
            self.__table.add(**{name: arr})


        def __delitem__(self, name):
            # FIXME
            try:
                self.__table.remove(name)
            except ValueError:
                raise KeyError(name)


        # Extensions beyond mapping API.

        @property
        def dtypes(self):
            return { n: c.arr.dtype for n, c in self.__cols.items() }


        # Table.cols.select proxy object ---------------------------------------

        class Select:

            def __init__(self, cols):
                self.__cols = cols


            def __repr__(self):
                return "Table.cols.select"


            def __call__(self, sel):
                names = container.select_ordered(self.__cols, sel, ctor=tuple)
                return Table({n: self.__cols[n] for n in names })
                    

            def __getitem__(self, key):
                if (
                    not isinstance(key, slice)
                    and (not hasattr(key, "__contains__") or isinstance(key, str))
                ):
                    key = (key, )
                return self.__call__(key)



        @memo.lazy_property
        def select(self):
            return self.Select(self.__cols)



    @memo.lazy_property
    def cols(self):
        return self.Cols(self)


    #---------------------------------------------------------------------------
    # Table.rows proxy object

    class Rows(collections.abc.Sequence):
        # FIXME: Allow modifying values in rows (i.e. mutable rows)?
        # FIXME: Allow inserting / removing rows (i.e. mutable sequence)?

        def __init__(self, table):
            self.__table = table
            self.__cols = table._Table__cols


        def __repr__(self):
            return repr(self.__table) + ".rows"


        def __len__(self):
            return self.__table._Table__length


        def __getitem__(self, sel):
            if np.isscalar(sel):
                # Return a single row.
                idx = py.normalize_index(sel, self.__table._Table__length)
                return Row(idx, self.__table._arrs)
            else:
                # Not a single index; return a subtable.
                return self.__table._Table__get_subtable(sel)


        def __iter__(self):
            arrs = self.__table._arrs
            return ( Row(i, arrs) for i in range(self.__table._Table__length) )



    @memo.lazy_property
    def rows(self):
        return self.Rows(self)


    #---------------------------------------------------------------------------
    # Mutators

    def add(self, *args, **kw_args):
        """
        Adds or replaces a column.
        """
        arrs = dict(*args, **kw_args)
        arrs = {
            str(n): _ensure_array(a, self.__length)
            for n, a in arrs.items() 
        }

        if len(arrs) == 0:
            # Nothing to do.
            return

        if len(self.__arrs) == 0:
            # This is the first column.
            self.__length = len(py.first_value(arrs))

        self.__arrs.update(arrs)


    def remove(self, *names):
        try:
            for name in names:
                try:
                    del self.__arrs[name]
                except KeyError:
                    raise ValueError(name)
        finally:
            if len(self.__arrs) == 0:
                # Removed the last column.
                self.__length = 0


    #---------------------------------------------------------------------------
    # Input/output

    show_max_rows = 24

    def _repr_html_(self):
        """
        HTML output hook for IPython / Jupyter.
        """
        from . import html
        return html.format_exc(html.render)(
            self, max_rows=self.show_max_rows)



#-------------------------------------------------------------------------------
# FIXME: Sugar.  Elsewhere.

import functools
import inspect

def collect(**cols):
    # FIXME: Make this work for series -> relation too.
    return Table(cols)


def col_fn(*, strict=False):
    """
    Wraps a function to apply to table cols.

        @col_fn()
        def foo(x, y):
            return x ** 2 + y

    The wrapped `foo` takes a single `Table` arg.  The table must have cols
    "x" and "y".  These are passed to `foo` as arrays.

    You may also call `foo` with keyword arguments, which supercede cols of the
    table arg.  If a keyword argument is given, or the param takes a default,
    the table need not contain the corresponding column.

    :param scrict:
      If true, the table arg may not have any columns not among the args; else
      raises `TypeError`.  You may also pass `strict` as a keyword argument when
      calling the wrapped fn.
    """
    def wrapper(fn):
        sig = inspect.signature(fn)
        if any(
                p.kind == inspect.Parameter.POSITIONAL_ONLY
                for p in sig.parameters.values()
        ):
            raise ValueError("fn may not have positional-only params")

        @functools.wraps(fn)
        def wrapped(table, *, strict=strict, **kw_args):
            if strict:
                extra = set(table.cols) - set(sig.parameters)
                if 0 < len(extra):
                    raise TypeError(f"unexpected args: {' '.join(extra)}")

            col_args = {
                n: a
                for n, a in table.cols.items()
                if n in sig.parameters
            }
            bound = sig.bind(**(col_args | kw_args))
            bound.apply_defaults()

            return fn(**bound.arguments)

        return wrapped

    return wrapper


