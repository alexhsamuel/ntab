"""
Pandas-lite tables, in a more numpy-oriented manner.
"""

#-------------------------------------------------------------------------------

from   __future__ import absolute_import, division, print_function, unicode_literals

from   builtins import *
import collections
from   collections import OrderedDict as odict
import numpy as np
import six
import sys

from   . import nplib
from   .lib import *

#-------------------------------------------------------------------------------

class ColsObjectProxy(object):
    """
    Proxy for arrays by name as attributes.
    """

    def __init__(self, table):
        self.__dict__.update(
            _ColsObjectProxy__table    =table,
            _ColsObjectProxy__arrays   =table._Table__arrays,
        )


    def __repr__(self):
        return repr(self.__table) + ".c"


    def __dir__(self):
        return list(self.__arrays.keys())


    def __getattr__(self, name):
        try:
            return self.__arrays[name]
        except KeyError:
            raise AttributeError(name)


    def __setattr__(self, name, array):
        self.__arrays[name] = self.__table._Table__as_array(array)
        self.__table._Table__update()


    def __delattr__(self, name):
        del self.__arrays[name]
        self.__table._Table__update()




class ColsProxy(collections.MutableMapping):
    """
    Mapping proxy for arrays by name.
    """

    def __init__(self, table):
        self.__table = table
        self.__arrays = table._Table__arrays


    def __repr__(self):
        return repr(self.__table) + ".cols"


    def __len__(self):
        return len(self.__arrays)


    def __iter__(self):
        return iter(self.__arrays)


    def keys(self):
        return self.__arrays.keys()


    def values(self):
        return self.__arrays.values()


    def items(self):
        return self.__arrays.items()


    def __getitem__(self, name):
        return self.__arrays[name]


    def __setitem__(self, name, array):
        self.__arrays[name] = self.__table._Table__as_array(array)
        self.__table._Table__update()


    def __delitem__(self, name):
        del self.__arrays[name]
        self.__table._Table__update()


    # Special methods.

    def select(self, names):
        """
        Returns a table with arrays selected by container `names`.
        """
        return self.__table.__class__(
            (n, a) for n, a in self.__arrays.items() if n in names )


    def renamed(self, names={}, **kw_args):
        """
        Returns a table with renamed arrays.
        """
        names = dict(names)
        names.update(kw_args)
        names = { o: n for n, o in names.items() }
        return self.__table.__class__(
            (names.get(n, n), a) for n, a in self.__arrays.items() )


    def sorted_as(self, *names):
        """
        Returns a table with the same arrays sorted as `names`.
        """
        names = sort_as(list(self.__arrays.keys()), names)
        return self.__table.__class__(
            (n, self.__arrays[n]) for n in names )



class RowsProxy(collections.Sequence):
    # FIXME: Allow modifying values in rows (i.e. mutable rows)?
    # FIXME: Allow inserting / removing rows (i.e. mutable sequence)?

    def __init__(self, table):
        self.__table = table
        self.__arrays = table._Table__arrays


    def __repr__(self):
        return repr(self.__table) + ".rows"


    def __len__(self):
        return self.__table.length


    def __getitem__(self, sel):
        if np.isscalar(sel):
            # Return a single row.
            return self.__table._get_row(int(sel))
        else:
            # Not a single index; return a subtable.
            return self.__table._Table__get_subtable(sel)


    def __iter__(self):
        Row = self.__table.Row
        return (
            Row(*r)
            for r in zip(*list(self.__table._Table__arrays.values()))
        )



#-------------------------------------------------------------------------------

# FIXME: Use `groupby.GroupBy`?

class GroupBy(collections.Mapping):

    def __init__(self, table, name):
        self.__table = table
        self.__array = table._Table__arrays[name]
        self.__name = name


    @property
    def __argunique(self):
        try:
            u = self.__cache
        except AttributeError:
            u = self.__cache = nplib.argunique(self.__array)
        return u


    def keys(self):
        _, unique, _ = self.__argunique
        return unique


    def values(self):
        order, _, edge = self.__argunique
        subtable = self.__table._take_rows
        for e0, e1 in zip(edge[: -1], edge[1 :]):
            yield subtable(order[e0 : e1])


    def items(self):
        order, unique, edge = self.__argunique
        subtable = self.__table._take_rows
        for u, e0, e1 in zip(unique, edge[: -1], edge[1 :]):
            yield u, subtable(order[e0 : e1])


    __iter__ = keys


    def __len__(self):
        _, unique, _ = self.__argunique
        return len(unique)


    def __getitem__(self, val):
        order, unique, edge = self.__argunique
        i = np.searchsorted(unique, val)
        if unique[i] == val:
            return self.__table._take_rows(order[edge[i] : edge[i + 1]])
        else:
            raise KeyError(val)



#-------------------------------------------------------------------------------

class Table(object):

    # Max number of rows to show in __str__.
    STR_MAX_ROWS = 16

    def __as_array(self, array):
        """
        Raises `ValueError` if `array` isn't valid for this table.
        """
        array = np.asarray(array)
        # if len(array.shape) != 1:
        #     raise ValueError("array must be one-dimensional")
        if array.shape[0] != self.__length:
            raise ValueError("array is the wrong length")
        return array


    def __update(self):
        """
        Call this when `__arrays` changes.
        """
        self.__Row = None


    def _get_row(self, idx):
        values = ( a[idx] for a in self.__arrays.values() )
        return self.Row(*values)


    def _take_rows(self, idxs):
        return self.__class__(
            # FIXME: a.take(idxs) _should_ be faster, but its 1000x slower if
            # a is not a contiguous array.
            (n, a[idxs]) for n, a in self.__arrays.items()
        )


    def __get_subtable(self, sel):
        return self.__class__(
            (n, a[sel]) for n, a in self.__arrays.items() )


    #---------------------------------------------------------------------------

    def __init__(self, arrays=()):
        self.__arrays = odict(arrays)
        self.__length = (
            0 if len(self.__arrays) == 0 
            else len(next(six.itervalues(self.__arrays)))
        )

        for name, array in self.__arrays.items():
            a = self.__as_array(array)
            if a is not array:
                self.__arrays[name] = a

        self.__Row      = None

        # Proxies.
        self.c          = ColsObjectProxy(self)
        self.cols       = ColsProxy(self)
        self.rows       = RowsProxy(self)


    def __repr__(self):
        return format_ctor(self, self.__arrays)


    def __str__(self):
        return "\n".join(self.format(max_length=self.STR_MAX_ROWS)) + "\n"


    def __reduce__(self):
        return self.__class__, (self.__arrays, )


    @property
    def Row(self):
        if self.__Row is None:
            self.__Row = collections.namedtuple("Row", list(self.__arrays.keys()))
        return self.__Row


    @property
    def length(self):
        return self.__length


    @property
    def names(self):
        return list(self.__arrays.keys())


    @property
    def dtypes(self):
        return self.Row(*( a.dtype for a in list(self.__arrays.values()) ))


    #---------------------------------------------------------------------------
    # Mutators
    # FIXME: Make immutable?

    def add(self, **arrs):
        bad_len = [ n for n, a in arrs.items() if len(a) != self.__length ]
        if len(bad_len) > 0:
            raise ValueError("wrong length: " + ", ".join(bad_len))
        self.__arrays.update(arrs)


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
            array = self.__arrays[name]
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


    def group_by(self, name):
        return GroupBy(self, name)


    #---------------------------------------------------------------------------
    # Factory methods

    @classmethod
    def from_array(class_, array):
        """
        Contructs from an array of records, such as a `np.recarray`.
        """
        return class_( (n, array[n]) for n in array.dtype.names )


    @classmethod
    def from_dataframe(class_, df):
        """
        Constructs from a `pandas.DataFrame`.
        """
        return class_( (n, df[n].values) for n in df.names )


    @classmethod
    def from_recs(class_, recs):
        """
        Constructs from an array of mapping records.

        All mappings must have the same keys.
        """
        recs = iter(recs)
        cols = odict( (n, [v]) for n, v in next(recs).items() )
        for rec in recs:
            for n, v in rec.items():
                cols[n].append(v)
        return class_( (n, np.array(v)) for n, v in cols.items() )


    #---------------------------------------------------------------------------
    # Conversion methods

    def as_dataframe(self):
        import pandas as pd
        return pd.DataFrame.from_items(self.__arrays.items())


    #---------------------------------------------------------------------------
    # Input/output

    # FIXME: This is horrible.  It will be rewritten.
    def format(self, max_length=32, header=True):
        def fmt(val):
            if isinstance(val, np.ndarray):
                return " ".join( str(a) for a in val )
            else:
                return str(val)

        names = list(self.__arrays.keys())
        arrays = list(self.__arrays.values())
        if max_length is not None:
            arrays = ( a[: max_length] for a in arrays )
        arrays = [ [ fmt(v) for v in a ] for a in arrays ]
        if len(arrays[0]) == 0:
            widths = [0] * len(arrays)
        else:
            widths = [ max( len(v) for v in c ) for c in arrays ]
        if header:
            widths = [ max(len(n), w) for n, w in zip(names, widths) ]
            yield " ".join( 
                "{:{}s}".format(n, w)
                for n, w in zip(names, widths)
            )
            yield " ".join( "-" * w for w in widths )
        if len(arrays[0]) == 0:
            yield "... empty table ..."
        for row in zip(*arrays):
            yield " ".join(
                "{:{}s}".format(v, w)
                for v, w in zip(row, widths)
            )
        if max_length is not None and max_length < self.__length:
            yield "... {} rows total ...".format(self.__length)


    def print(self, **kw_args):
        for line in self.format(**kw_args):
            print(line)


    CSS = """
    .tab-table {
      font-size: 80%;
      line-height: 70%;
    }
    .tab-table thead {
      background: #e0e0e0;
      line-height: 120%;
    }
    .tab-table td, .tab-table th, .tab-table tr {
      border-color: #f0f0f0;
      border-style: none dotted;
    }
    .tab-table tbody {
      font-family: Consolas, monospace;
    }
    table.tab-table {
      border-collapse: collapse;
      border: none;
    }
    """

    def format_html_table(self, max_length=16, css_class="tab-table"):
        """
        Renders the table as an HTML table element.

        @return
          A generator of HTML source strings.
        """
        from cgi import escape

        names = list(self.__arrays.keys())
        arrays = list(self.__arrays.values())
        if max_length is not None:
            arrays = [ a[: max_length] for a in arrays ]
        aligns = [
            "left" if a.dtype.kind in {"U", "S"} else "right"
            for a in arrays
        ]

        arrays = [ [ str(v) for v in a ] for a in arrays ]

        yield "<table class='{}'>".format(escape(css_class))
        yield "<thead>"
        yield "<tr>"
        for name in names:
            yield "<th>" + escape(name) + "</th>"
        yield "</tr>"
        yield "</thead>"
        yield "<tbody>"
        if self.__length == 0:
            yield "<tr>"
            yield "<td colspan='{}' style='text-align: center'>... empty ...</td>".format(len(names))
            yield "</tr>"
        else:
            for row in zip(*arrays):
                yield "<tr>"
                for val, align in zip(row, aligns):
                    yield "<td style='text-align: {};'>{}</td>".format(
                        align, escape(val))
                yield "</tr>"
        if max_length is not None and max_length < self.__length:
            yield "<tr>"
            yield "<td colspan='{}' style='text-align: center'>... {} rows total ...</td>".format(
                len(names), self.__length)
            yield "</tr>"
        yield "</tbody>"
        yield "</table>"
        

    def _repr_html_(self):
        """
        HTML output hook for IPython / Jupyter.
        """
        # IPython silently ignores exceptions raised from here, which is 
        # really confusing.  Instead, catch and format them.
        try:
            return "".join(self.format_html_table())
        except:
            import cgi, traceback
            return (
                "<b>exception in <code>Table._repr_html_</code>:</b>"
                "<pre>" + cgi.escape(traceback.format_exc()) + "</pre>"
            )



