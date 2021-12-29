import collections.abc

from   . import fmt
from   .column import Column
from   .lib import text

#-------------------------------------------------------------------------------

class Series(collections.abc.Mapping):

    def __init__(self, col, index, name="rel"):
        col = Column.wrap(col)
        length = len(col.arr)
        if len(index.rows) != length:
            raise ValueError("wrong length index")

        self.__index = index
        self.__col = col
        self.__name = str(name)


    def __str__(self):
        sorter = self.__index.sorter
        arrs = (
            [ (n, a[sorter]) for n, a in self.__index.cols.items() ]
            + [(self.__name, self.__col.arr[sorter])]
        )
        return text.join_lines(fmt.format_arrs(
            arrs,
            num_index=len(self.__index.cols)
        ))


    @property
    def col(self):
        return self.__col.arr


    @property
    def index(self):
        return self.__index


    @property
    def name(self):
        return self.__name


    #---------------------------------------------------------------------------
    # Mapping

    def __len__(self):
        return len(self.__index)


    def __iter__(self):
        return iter(self.__index)


    def keys(self):
        return self.__index.keys()


    def values(self):
        return iter(self.__col.arr)


    def items(self):
        return zip(self.__index, self.__col.arr)


    def __getitem__(self, sel):
        # FIXME: Slicing.
        return self.__col.arr[self.__index[sel]]





