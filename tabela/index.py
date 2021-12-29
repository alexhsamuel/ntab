import collections.abc
import numpy as np
import re

from   .column import Column
from   .lib import memo, py, text
from   . import fmt

#-------------------------------------------------------------------------------

# FIXME: Could share a common base class with Table.
class Index:

    def __init__(self, cols):
        cols = { str(n): Column.wrap(c) for n, c in cols.items() }
        if len(cols) == 0:
            raise ValueError("no cols")
        length = len(py.first_value(cols).arr)
        if any( len(c.arr) != length for c in cols.values() ):
            raise ValueError("not the same length")

        self.__length = length
        self.__cols = cols

        # Check uniqueness.
        # FIXME: Performance: Do this as part of multisort.
        s = self.sorter
        m = np.arange(len(s) - 1)
        for c in self.__cols.values():
            m = m[c.arr[s[m]] == c.arr[s[m + 1]]]
        if len(m) > 0:
            i = s[m[0]]
            val = tuple( c.arr[i] for c in self.__cols.values() )
            raise ValueError(f"not unique: {val}")


    def __repr__(self):
        return py.format_ctor(
            self,
            {
                # Remove newlines from NumPy's reprs.
                n: re.sub(r"\s+", " ", repr(c.arr))
                for n, c in self.__cols.items()
            }
        )


    def __str__(self):
        sorter = self.sorter
        return text.join_lines(fmt.format_arrs(
            ( (n, c.arr[sorter]) for n, c in self.__cols.items() ),
            num_index=len(self.__cols),
        ))


    @property
    def cols(self):
        return { n: c.arr for n, c in self.__cols.items() }


    # Rows proxy ---------------------------------------------------------------

    class Rows(collections.abc.Mapping):

        def __init__(self, index):
            self.__index = index
            self.__length = index._Index__length
            self.__arrs = [ c.arr for c in index._Index__cols.values() ]
            

        def __len__(self):
            return self.__length


        def __iter__(self):
            return zip(*self.__arrs)


        keys = __iter__


        def values(self):
            return range(self.__length)


        def items(self):
            return ( (k, i) for i, k in enumerate(self.keys()) )


        def __getitem__(self, key):
            # FIXME: Slicing.

            # FIXME: Performance: sorter + multisearchsorted.
            s = i0 = i1 = None
            for k, a in zip(py.tupleize(key), self.__arrs, strict=True):
                s = self.__index.sorter if s is None else s[i0 : i1]
                a = a[s]
                i0 = np.searchsorted(a, k, side="left")
                if a[i0] != k:
                    break
                i1 = np.searchsorted(a, k, side="right")
                if i0 == i1:
                    break
            else:
                assert i1 - i0 == 1
                return s[i0]
            raise KeyError(key)



    @memo.lazy_property
    def rows(self):
        return self.Rows(self)


    #---------------------------------------------------------------------------

    @memo.lazy_property
    def sorter(self):
        """
        Returns an idx array that sorts the index columns.
        """
        # FIXME: Performance: need multisort.
        cols = tuple(self.__cols.values())[:: -1]
        sorter = cols[0].sorter
        for col in cols[1 :]:
            sorter = sorter[np.argsort(col.arr[sorter], kind="stable")]
        # FIXME: Use a narrower dtype, if it fits.
        return sorter
            
        

