import collections.abc

from   .index import Index
from   .lib import memo, py, text
from   .series import Series
from   .table import Row
from   . import fmt

NO_DEFAULT = object()

#-------------------------------------------------------------------------------

class Relation:

    def __init__(self, index, table):
        # FIXME
        assert isinstance(index, Index)

        # FIXME: Detect name collisions with different values between cols and index.
        if len(index.rows) != len(table.rows):
            raise ValueError("index and table not the same length")

        self.__index = index
        self.__table = table


    def __repr__(self):
        return py.format_ctor(self, self.__index, self.__table)


    STR_MAX_ROWS = 16

    def __str__(self):
        return text.join_lines(_format(self))


    @property
    def index(self):
        return self.__index


    @property
    def table(self):
        return self.__table


    # Cols proxy ---------------------------------------------------------------

    class Cols(collections.abc.MutableMapping):
        def __init__(self, relation):
            self.__relation = relation
            self.__cols = relation.table.cols
            self.__index = relation.index


        def __repr__(self):
            # FIXME
            return "Cols(...)"


        def __len__(self):
            return len(self.__cols)


        def __iter__(self):
            return iter(self.__cols)


        def keys(self):
            return self.__cols.keys()


        def values(self):
            return ( Series(c, self.__index, n) for n, c in self.__cols.items() )


        def items(self):
            return ( (n, Series(c, self.__index, n)) for n, c in self.__cols.items() )


        def get(self, key, /, default=NO_DEFAULT) -> Series:
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
                        name, col = tuple(self.__cols.items())[idx]
                        return Series(col, self.__index, name)
                    except IndexError:
                        if default is NO_DEFAULT:
                            raise KeyError(idx) from None
                        else:
                            return default
            # Try as str name.
            try:
                name = str(key)
                col = self.__cols[name]
            except KeyError:
                if default is NO_DEFAULT:
                    raise
                else:
                    return default
            else:
                return Series(col, self.__index, name)


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
            return { n: a.dtype for n, a in self.__cols.items() }


        # Relation.cols.select proxy object ------------------------------------

        class Select:

            def __init__(self, index, table):
                self.__index = index
                self.__table = table


            def __repr__(self):
                return "Relation.cols.select"


            def __call__(self, sel):
                return Relation(self.__index, self.__table.cols.select(sel))


            def __getitem__(self, key):
                return Relation(self.__index, self.__table.cols.select.__getitem__(key))
            


        @memo.lazy_property
        def select(self):
            return self.Select(self.__index, self.__relation.table)


    @memo.lazy_property
    def cols(self):
        return self.Cols(self)


    # Rows proxy ---------------------------------------------------------------

    class Rows(collections.abc.Mapping):

        __slots__ = (
            "__index_rows",
            "__arrs",
        )

        def __init__(self, index_rows, arrs):
            self.__index_rows = index_rows
            self.__arrs = arrs


        def __repr__(self):
            return "Relation.Rows()"


        def __len__(self):
            return len(self.__index_rows)


        def __iter__(self):
            return iter(self.__index_rows)


        def keys(self):
            return self.__index_rows.keys()


        def values(self):
            arrs = self.__arrs
            return ( Row(i, arrs) for i in range(len(self.__index_rows)) )


        def items(self):
            arrs = self.__arrs
            return (
                (k, Row(i, arrs))
                for i, k in enumerate(self.__index_rows)
            )


        def __getitem__(self, sel):
            # FIXME: Slicing.
            return Row(self.__index_rows[sel], self.__arrs)



    @memo.lazy_property
    def rows(self):
        return self.Rows(self.__index.rows, self.__table._arrs)



def _format(rln, *, dedup_index=True):
    """
    :param dedup_index:
      If true, omit cols that also appear in the index.
    """
    sorter = rln.index.sorter
    arrs = (
        [
            (n, a[sorter])
            for n, a in rln.index.cols.items()
        ]
        + [
            (n, s.col[sorter]) 
            for n, s in rln.cols.items()
            if not (dedup_index and n in rln.index.cols)  # FIXME: AND is same column.
        ]
    )
    lines = fmt.format_arrs(
        arrs,
        max_length=rln.STR_MAX_ROWS,
        num_index=len(rln.index.cols),
    )
    return lines



def index(table, by):
    index = Index({ n: table.cols[n] for n in py.iterize(by) })
    return Relation(index, table)


