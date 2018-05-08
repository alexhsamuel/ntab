"""
Pandas-lite tables, in a more numpy-oriented manner.
"""

#-------------------------------------------------------------------------------

from   __future__ import absolute_import, division, print_function, unicode_literals

import collections
import numpy as np

from   . import fmt
from   .lib import sort_as, normalize_index, format_ctor, a_value

__all__ = (
    "Table",
    "from_array",
    "from_dataframe",
    "from_recs",
)

#-------------------------------------------------------------------------------

def _ensure_array(obj, length):
    """
    Ensures `obj` is an ndarray of shape `(length, )`, converting if necessary.
    """
    arr = None

    if isinstance(obj, np.ndarray):
        arr = obj

    if arr is None and not isinstance(obj, (bytes, str)):
        # Convert sequences to arrays.
        try:
            len(obj)
        except:
            pass
        else:
            arr = np.array(obj)
            
    # Convert scalars to full arrays.
    if arr is None:
        # FIXME: Newer numpy doesn't require explicit dtype
        dtype = np.array(obj).dtype
        arr = np.full(length, obj, dtype)
    
    if len(arr.shape) != 1:
        raise ValueError("not one-dimensional")
    if length is not None and arr.shape != (length, ):
        raise ValueError("wrong length")
    return arr


#-------------------------------------------------------------------------------

class ArraysObjectProxy(object):
    """
    Proxy for arrays by name as attributes.
    """

    def __init__(self, table):
        self.__dict__.update(
            _ArraysObjectProxy__table    =table,
            _ArraysObjectProxy__arrs     =table._Table__arrs,
        )


    def __repr__(self):
        return repr(self.__table) + ".c"


    def __dir__(self):
        return list(self.__arrs.keys())


    def __getattr__(self, name):
        try:
            return self.__arrs[name]
        except KeyError:
            raise AttributeError(name)


    def __setattr__(self, name, array):
        self.__table.add(**{name: array})


    def __delattr__(self, name):
        try:
            self.__table.remove(name)
        except ValueError:
            raise AttributeError(name)




class ArraysProxy(collections.MutableMapping):
    """
    Mapping proxy for arrays by name.
    """

    def __init__(self, table):
        self.__table = table
        self.__arrs = table._Table__arrs


    def __repr__(self):
        return repr(self.__table) + ".cols"


    def __len__(self):
        return len(self.__arrs)


    def __iter__(self):
        return iter(self.__arrs)


    def keys(self):
        return self.__arrs.keys()


    def values(self):
        return self.__arrs.values()


    def items(self):
        return self.__arrs.items()


    def __getitem__(self, name):
        return self.__arrs[name]


    def __setitem__(self, name, array):
        self.__table.add(**{name: array})


    def __delitem__(self, name):
        try:
            self.__table.remove(name)
        except ValueError:
            raise KeyError(name)


    # Special methods.

    def select(self, names):
        """
        Returns a table with arrays selected by container `names`.
        """
        return self.__table.__class__(
            (n, a) for n, a in self.__arrs.items() if n in names )


    def renamed(self, names={}, **kw_args):
        """
        Returns a table with renamed arrays.
        """
        names = dict(names)
        names.update(kw_args)
        names = { o: n for n, o in names.items() }
        return self.__table.__class__(
            (names.get(n, n), a) for n, a in self.__arrs.items() )


    def sorted_as(self, *names):
        """
        Returns a table with the same arrays sorted as `names`.
        """
        names = sort_as(list(self.__arrs.keys()), names)
        return self.__table.__class__(
            (n, self.__arrs[n]) for n in names )



class Row(object):

    def __init__(self, arrs, idx):
        self.__arrs = arrs
        self.__arrs_seq = tuple(arrs.values())
        self.__idx = idx


    def __len__(self):
        return len(self.__arrs)


    def __iter__(self):
        return ( a[self.__idx] for a in self.__arrs.values() )


    def __getitem__(self, idx):
        return self.__arrs_seq[idx][self.__idx]


    # FIXME: Is this a good idea?
    def __dir__(self):
        return list(self.__arrs)


    def __getattr__(self, name):
        try:
            arr = self.__arrs[name]
        except KeyError:
            raise AttributeError(name) from None
        else:
            return arr[self.__idx]


    def __repr__(self):
        return (
            "Row({}, ".format(self.__idx)
            + ", ".join( 
                "{}={!r}".format(n, a[self.__idx])
                for n, a in self.__arrs.items())
            + ")"
        )

    
    def __str__(self):
        return "\n".join(fmt.format_row(self))


    def _repr_html_(self):
        from . import html
        return html.format_exc(html.render_row)(self)


    @property
    def __idx__(self):
        return self.__idx


    # FIXME: Potentially sketchy.
    @property
    def __dict__(self):
        return { n: a[self.__idx] for n, a in self.__arrs.items() }



class RowsProxy(collections.Sequence):
    # FIXME: Allow modifying values in rows (i.e. mutable rows)?
    # FIXME: Allow inserting / removing rows (i.e. mutable sequence)?

    def __init__(self, table):
        self.__table = table
        self.__arrs = table._Table__arrs


    def __repr__(self):
        return repr(self.__table) + ".rows"


    def __len__(self):
        return self.__table.num_rows


    def __getitem__(self, sel):
        if np.isscalar(sel):
            # Return a single row.
            idx = normalize_index(sel, self.__table.num_rows)
            return self.__table._get_row(idx)
        else:
            # Not a single index; return a subtable.
            return self.__table._Table__get_subtable(sel)


    def __iter__(self):
        get_row = self.__table._get_row
        return ( get_row(i) for i in range(self.__table.num_rows) )



#-------------------------------------------------------------------------------

class Table(object):
    """
    Data table consisting of named parallel `ndarray`s.

    A table consists of zero or more arrays, representing columns, each of which
    must be one-dimensional and of the same length.  The column arrays are taken
    to be parallel: each "row" of the tabel consists of corresponding elements
    of the column arrays.
    """

    # Max number of rows to show in __str__.
    STR_MAX_ROWS = 16

    def _get_row(self, idx):
        return Row(self.__arrs, idx)


    def _take_rows(self, idxs):
        return self.__class__(
            # FIXME: a.take(idxs) _should_ be faster, but its 1000x slower if
            # a is not a contiguous array.
            (n, a[idxs]) for n, a in self.__arrs.items()
        )


    def __get_subtable(self, sel):
        return self.__class__(
            (n, a[sel]) for n, a in self.__arrs.items() )


    def __construct(self, length, arrs):
        self.__length = length
        self.__arrs = arrs
        # Proxies.
        # FIXME: Create lazily?
        self.a          = ArraysObjectProxy(self)
        self.arrs       = ArraysProxy(self)
        self.rows       = RowsProxy(self)


    def __check(self, arrs):
        for name, arr in arrs.items():
            if not isinstance(name, str):
                raise TypeError("not a string name: {}".format(name))
            if not isinstance(arr, np.ndarray):
                raise TypeError("not an ndarray: {}".format(name))
            if len(arr.shape) != 1:
                raise ValueError("not 1-dimensional array: {}".format(name))
            if self.__length is not None and arr.shape != (self.__length, ):
                raise ValueError("wrong length: {}".format(name))


    #---------------------------------------------------------------------------

    def __init__(self, *args, **kw_args):
        """
        Constructs a new table from named parallel arrays.

        Arguments are anything that can construct a `dict` from column name
        to array:

        - A mapping object from names to arrays.
        - An iterable of name, array pairs.
        - Name, array keyword arguments.

        Array arguments are converted to `ndarray`, if necessary.  They must all
        be one-dimensional and the same length.
        """
        arrs = dict(*args, **kw_args)

        # Get the length.
        length = None
        for arr in arrs.values():
            try:
                length = len(arr)
            except TypeError:
                pass
            else:
                break
        if length is None and len(arrs) > 0:
            raise ValueError("no arrs have length")

        # Make sure the arrays are all arrays.
        arrs = dict(
            (str(n), _ensure_array(a, length)) 
            for n, a in arrs.items() 
        )

        self.__construct(length, arrs)
        self.__check(self.__arrs)


    @classmethod
    def wrap(class_, arrs, check=True):
        """
        Constructs a table by wrapping a mapping from names to parallel array.

        @param arrs
          A mapping object from string names to parallel `ndarray`s.  The table
          henceforth owns the mapping; if the table is mutated, the mapping
          will be as well.
        @param check
          If true, check that `arrs` honors the above.  If not, no check is
          done, but if the `arrs` are the wrong type, undefined behavior may
          occur later.
        """
        # Construct an instance without calling __init__().
        self = object.__new__(class_)

        self.__construct(arrs)
        if check:
            self.__check(self.__arrs)
        return self


    #---------------------------------------------------------------------------

    def __repr__(self):
        return format_ctor(self, self.__arrs)


    def __str__(self):
        return (
              "\n".join(fmt.format_table(self, max_length=self.STR_MAX_ROWS)) 
            + "\n"
        )


    def __reduce__(self):
        return self.__class__, (self.__arrs, )


    @property
    def num_rows(self):
        return 0 if self.__length is None else self.__length


    @property
    def num_cols(self):
        return len(self.__arrs)


    @property
    def names(self):
        return list(self.__arrs.keys())


    @property
    def dtypes(self):
        return Row({ n: [a.dtype] for n, a in self.__arrs.items() }, 0)


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
            self.__length = len(a_value(arrs))

        self.__check(arrs)

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
    # Special methods

    def mask(self, mask):
        # FIXME: We could store the mask in the table, and apply it lazily.
        mask = np.asarray(mask, dtype=bool)
        if mask.shape != (self.__length, ):
            raise ValueError("wrong shape")
        return self.__get_subtable(mask)


    def filter_mask(self, **selections):
        mask = None
        for name, value in selections.items():
            array = self.__arrs[name]
            if mask is None:
                mask = array == value
            else:
                mask[mask] &= array[mask] == value
        return mask


    def filter(self, **selections):
        return self.mask(self.filter_mask(**selections))


    def find(self, **selections):
        idx = self.filter_mask(**selections).nonzero()[0]
        if len(idx) == 0:
            raise LookupError("no item")
        elif len(idx) == 1:
            return self._get_row(idx)
        else:
            raise LookupError("multiple items")


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
# Construction functions

def from_array(array, Table=Table):
    """
    Contructs a table from a structured array or recarray.
    """
    return Table( (n, array[n]) for n in array.dtype.names )


def from_dataframe(df, Table=Table):
    """
    Constructs a table from a `pandas.DataFrame`.
    """
    return Table( (n, df[n].values) for n in df.names )


def from_recs(recs, Table=Table):
    """
    Constructs a table from an array of mapping records.

    All mappings must have the same keys.
    """
    # FIXME: There are much faster implementations for this.
    recs = iter(recs)
    cols = { n: [v] for n, v in next(recs).items() }
    for rec in recs:
        for n, v in rec.items():
            cols[n].append(v)
    return Table( (n, np.array(v)) for n, v in cols.items() )


#-------------------------------------------------------------------------------
# Conversion methods

def to_dataframe(tab):
    """
    Converts the table to a Pandas dataframe.
    """
    import pandas as pd
    return pd.DataFrame.from_items(tab.arrs.items())


