from   __future__ import absolute_import, division, print_function, unicode_literals

import collections
import logging as log  # FIXME
import numpy as np

#-------------------------------------------------------------------------------

NAT = np.datetime64("nat")

def get_dtype(name, val):
    try:
        return val.dtype
    except AttributeError:
        return np.array([val]).dtype


def resize(arr, size):
    assert size > len(arr)
    default = default_for_dtype(arr.dtype)
    new_arr = np.full(size, default, dtype=arr.dtype)
    new_arr[: len(arr)] = arr
    return new_arr


class RecAccumulator(object):

    def __init__(self, size_hint=1024):
        self.__cols = {}
        self.__length = 0
        self.__size = size_hint


    def append(self, **rec):
        if self.__length == self.__size:
            self.__size *= 4
            log.debug("resizing columns: {}".format(self.__size))
            self.__cols = { 
                n: resize(a, self.__size) 
                for n, a in self.__cols.items() 
            }

        for name, val in rec.items():
            try:
                arr = self.__cols[name]
            except KeyError:
                dtype = np.dtype(get_dtype(name, val))
                if dtype.kind in ("S", "U"):
                    # Don't use fixed-length strings, as subsequent values
                    # may not fit (and will be truncated).
                    dtype = np.dtype(object)
                log.debug("new column: {} [{}]".format(name, dtype))
                default = default_for_dtype(dtype)
                arr = self.__cols[name] \
                    = np.full(self.__size, default, dtype=dtype)
            arr[self.__length] = val
        self.__length += 1


    @property
    def arrays(self):
        return { n: a[: self.__length] for n, a in self.__cols.items() }
        


def arrs_from_recs(recs, size_hint=1024, get_dtype=get_dtype):
    """
    Transposes an iterable of mappings to a mapping of arrays.

      >>> recs = [
      ...   dict(x=10.0, y=20.0, z=30.0),
      ...   dict(x=12.0, y=42.0),
      ...   dict(x=19.5, y=57.3, z=1042)]
      >>> arrs = arrs_from_recs(recs)
      >>> arrs["x"]
      array([ 10. ,  12. ,  19.5])
      >>> arrs["y"]
      array([ 20. ,  42. ,  57.3])
      >>> arrs["z"]
      array([   30.,    nan,  1042.])

    """
    def resize(arr, size):
        assert size > len(arr)
        default = default_for_dtype(arr.dtype)
        new_arr = np.full(size, default, dtype=arr.dtype)
        new_arr[: len(arr)] = arr
        return new_arr

    cols = {}
    length = 0
    size = size_hint
    for rec in recs:
        if length == size:
            size *= 4
            log.debug("resizing columns: {}".format(size))
            cols = { n: resize(a, size) for n, a in cols.items() }

        for name, val in rec.items():
            try:
                arr = cols[name]
            except KeyError:
                dtype = np.dtype(get_dtype(name, val))
                log.debug("new column: {} [{}]".format(name, dtype))
                default = default_for_dtype(dtype)
                arr = cols[name] = np.full(size, default, dtype=dtype)
            arr[length] = val
        length += 1

    return { n: a[: length] for n, a in cols.items() }


def default_for_dtype(dtype):
    if dtype.kind == "i":
        return np.iinfo(dtype).min  # Sadness.
    else:
        return {
            "b": False,   # Very sadness.
            "f": np.nan,
            "M": NAT,
            "O": None,
            "S": "",
        }[dtype.kind]


#-------------------------------------------------------------------------------
# Grouping functions

def join_groups(arrs, on):
    """
    Generates sub-recarrays by value of field `on`.

    @param arrs
      A sequence of one or more recarrays.
    @param on
      A column name, or a sequence of column names corresponding to `arrs`.
    @return
      A generator of `value, subarrs` pairs, where `value` is the group value
      and `subarrs` are corresponding subarrays of `arrs`.
    """
    n = len(arrs)
    if isinstance(on, str):
        on = (on, ) * n
    else:
        on = py.tupleize(on)
    assert len(on) == n

    # Fish out the arrays we'll be grouping on.
    group_arrs = [ getattr(a, o) for a, o in zip(arrs, on) ]

    indexes = [0] * n
    next_grps = [ 
        g[i] if i < len(g) else None 
        for g, i in zip(group_arrs, indexes) 
    ]

    while True:
        grp = [ g for g in next_grps if g is not None ]
        if len(grp) == 0:
            break
        grp = min(grp)
        subarrs = []
        for i in range(n):
            idx = indexes[i]
            group_arr = group_arrs[i]
            g = group_arr[idx]
            arr = arrs[i]
            if g == grp:
                # Scan forward.
                next_idx = idx
                # FIXME: Assert non-decreasing.
                while next_idx < len(group_arr) and group_arr[next_idx] == g:
                    next_idx += 1
                subarrs.append(arr[idx : next_idx])
                indexes[i] = next_idx
                next_grps[i] = (
                    group_arr[next_idx] if next_idx < len(arr) else None
                )

            else:
                subarrs.append(arr[0 : 0])

        yield grp, subarrs


def map_groups(arrs, on, fn):
    """
    Groups sub-recarrays by value of field `on`, and invokes `fn` on each group.
    """
    return ( fn(g, *a) for g, a in join_groups(arrs, on) )


def argunique(arr, order=None):
    """
    @return
      `order, groups, edges`, where `order` is the stable sort order, `unique`
      is the array of sorted unique values, and `edges` is an array giving the
      start index in `order` for each unique value.
    """
    if len(arr) == 0:
        e = np.array((), dtype=int)
        return e, arr, e

    if order is None:
        order = np.argsort(arr, kind="mergesort")

    sort    = arr[order]
    edge    = np.concatenate(([True], sort[1 :] != sort[: -1]))
    unique  = sort[edge]
    edge,   = edge.nonzero()
    edge    = np.concatenate((edge, [len(arr)]))
    return order, unique, edge


def arguniquen(arrays, orders=None):
    """
    Finds sets of unique values across a number of arrays.

    Returns:

    - Sort `orders` for the arrays.  These may also be passed in, if available.
    - A array of sorted `unique` values across all `arrays`.
    - A 2D array `edges` locating the positions of the unique values in the
      `arrays`.  The first dimension corresponds to the unique values; the
      second to the arrays.  Each value is the position _in the sorted array_
      where unique values start.

    The `i`th unique value is `unique[i]`.  The indices of this value in
    the `j`th array are `orders[j][edges[i][j] : edges[i + 1][j]]`.

    The invariant is,

    ```
    u = unique[i]
    a = arrays[j]
    idxs = orders[j][edges[i][j] : edges[i + 1][j]]
    (a[idxs] == u).all()
    ```

    @param arrays
      One or more arrays, of the same time, to find unique values in.
    @param orders
      If available, stable sort orders for the `arrays`; if `None`, these are
      computed.
    @return
      `orders, unique, edges`.
    """
    num = len(arrays)
    if num == 0:
        raise ValueError("no arrays given")

    if orders is None:
        orders = [None] * num
    orders = [
        np.argsort(a, kind="mergesort") if o is None else o
        for a, o in zip(arrays, orders)
    ]

    lengths = np.array([ len(a) for a in arrays ])
    arr = np.concatenate(arrays)

    # Special case: no elements at all.
    if len(arr) == 0:
        e = np.array((), dtype=int)
        return (e, ) * num, arr, (e, ) * num

    # FIXME: Use `orders` to do this in linear time.
    order   = np.argsort(arr, kind="mergesort")
    sort    = arr[order]
    edge    = np.concatenate(([True], sort[1 :] != sort[: -1]))
    unique  = sort[edge]
    edge,   = edge.nonzero()

    # Construct an array identifying which sorted value is from which array.
    which   = np.repeat(np.arange(num), lengths)[order]
    if True:  # FIXME: unravel_groups is faster!
        # Slice this up by unique value, and count how many from which array.
        ref     = np.arange(num)[:, np.newaxis]
        edges   = [ (o == ref).sum(axis=1) for o in np.split(which, edge) ]
        # For convenience, tack on an extra edge row with the length of each array.
        edges.append(lengths)
        # The cumsum of these gives positions in the individual order arrays.
        edges   = np.vstack(edges).cumsum(axis=0)
    else:
        import nputil
        edges = nputil.unravel_groups(num, which, edge).cumsum(axis=0)

    return orders, unique, edges


#-------------------------------------------------------------------------------

class MultiGroupBy(collections.Mapping):

    def __init__(self, *arrays):
        self.__arrays       = tuple(arrays)


    @property
    def __argunique(self):
        """
        Lazily performs the real work, and caches the result.
        """
        try:
            u = self.__cache
        except AttributeError:
            u = self.__cache = arguniquen(self.__arrays)
        return u


    def keys(self):
        _, unique, _ = self.__argunique
        return unique


    def iterkeys(self):
        return iter(list(self.keys()))


    def itervalues(self):
        """
        Generates groups.

        Each group is a `val, subtables` pair, where `val` is the group value
        and `subtables` is a sequence of subtables for that group.
        """
        orders, _, edges = self.__argunique
        for edge0, edge1 in zip(edges[: -1], edges[1 :]):
            yield [
                o[i0 : i1] for o, i0, i1 in zip(orders, edge0, edge1)
            ]


    def values(self):
        # This is not advisable, but...
        return list(self.values())


    def iteritems(self):
        return zip(iter(self.keys()), iter(self.values()))


    def items(self):
        # This is not advisable, but...
        return list(self.items())


    def __len__(self):
        _, unique, _ = self.__argunique
        return len(unique)


    def __getitem__(self, val):
        orders, unique, edges = self.__argunique
        i = np.searchsorted(unique, val)
        if unique[i] == val:
            return [
                o[i0 : i1] for o, i0, i1 in zip(orders, edges[i], edges[i + 1])
            ]
        else:
            raise KeyError(val)


    __iter__ = iterkeys

    #---------------------------------------------------------------------------

    def map(self, fn, *arrays):
        if len(arrays) != len(self.__arrays):
            raise TypeError("wrong number of arguments")
        if any( len(a) != len(aa) for a, aa in zip(arrays, self.__arrays) ):
            raise ValueError("wrong array lengths")

        return ( 
            fn(u, *( a[i] for a, i in zip(arrays, idxs) )) 
            for u, idxs in self.items() 
        )



