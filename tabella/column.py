import numpy as np

from   .lib import memo, nplib, py

#-------------------------------------------------------------------------------

class Column:

    def __init__(self, arr):
        self.arr = np.asarray(arr)
        if self.arr.ndim != 1:
            raise ValueError("not one-dimensional")


    def __repr__(self):
        return py.format_ctor(self, self.arr)


    def __str__(self):
        return str(self.arr)


    def __eq__(self, other):
        return (
            other is self
            or (
                nplib.same(self, other) if isinstance(other, Column)
                else NotImplemented
            )
        )
            

    @classmethod
    def wrap(cls, obj):
        if isinstance(obj, cls):
            return obj
        else:
            return cls(obj)


    @memo.lazy_property
    def sorter(self):
        return np.argsort(self.arr, kind="stable")



