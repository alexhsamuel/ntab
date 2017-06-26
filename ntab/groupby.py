from   __future__ import absolute_import, division, print_function, unicode_literals

from   builtins import *
import collections
import numpy as np

from   .lib import tupleize
from   . import nplib

#-------------------------------------------------------------------------------

class GroupBy(collections.Mapping):

    def __init__(self, table, name):
        self.__table    = table
        self.__arr      = table.arrs[name]
        self.__name     = name
        self.__cache    = None


    @property
    def __argunique(self):
        if self.__cache is None:
             self.__cache = nplib.argunique(self.__arr)
        return self.__cache


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

class MultiGroupBy(collections.Mapping):

    def __init__(self, tables, names):
        tables = tupleize(tables)
        num = len(tables)
        if isinstance(names, str):
            names = (names, ) * num
        else:
            names = tupleize(names)
            if len(names) != num:
                raise ValueError("wrong number of names")

        self.__tables   = tables
        self.__names    = names
        self.__arrays   = [ t.arrays[n] for t, n in zip(tables, names) ]
        self.__cache    = None


    @property
    def __argunique(self):
        """
        Lazily performs the real work, and caches the result.
        """
        if self.__cache is None:
            self.__cache = nplib.arguniquen(self.__arrays)
        return self.__cache


    def __len__(self):
        _, unique, _ = self.__argunique
        return len(unique)


    def __getitem__(self, val):
        orders, unique, edges = self.__argunique
        i = np.searchsorted(unique, val)
        if unique[i] == val:
            return [
                t._take_rows(o[i0 : i1])
                for t, o, i0, i1 
                in zip(self.__tables, orders, edges[i], edges[i + 1])
            ]
        else:
            raise KeyError(val)


    def keys(self):
        _, unique, _ = self.__argunique
        return unique


    __iter__ = keys

    def itervalues(self):
        """
        Generates groups.

        Each group is a `val, subtables` pair, where `val` is the group value
        and `subtables` is a sequence of subtables for that group.
        """
        orders, _, edges = self.__argunique
        take = [ t._take_rows for t in self.__tables ]
        for edge0, edge1 in zip(edges[: -1], edges[1 :]):
            yield [
                t(o[i0 : i1])
                for t, o, i0, i1 in zip(take, orders, edge0, edge1)
            ]


    def iteritems(self):
        return zip(iter(self.keys()), iter(self.values()))



