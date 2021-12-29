"""
Containers.

A container is an object that supports `__contains__`. 
"""

import collections.abc
import re

from   . import py

#-------------------------------------------------------------------------------

def is_container(obj):
    return hasattr(obj, "__contains__") and not py.is_str(obj)


def select(items, container, *, ctor=None):
    """
    Returns `items` that are in `container`.

    :param ctor:
      Constructor for returned value.  If `None`, uses the type of `items`.
      Use `iter` to return an iterable.
    """
    if ctor is None:
        ctor = type(items)

    return ctor( i for i in items if i in container )


def select_ordered(items, container, *, ctor=None):
    """
    Returns `items` that are in `container`.

    If `container` is a sequence, returns them in the order they appear there.
    """
    if ctor is None:
        ctor = type(items)

    if isinstance(container, collections.abc.Sequence):
        # A frozenset would be more efficient, but there's no guarantee that
        # the items are hashable.
        members = tuple(items)
        # Expand ellipsis.
        try:
            e = container.index(Ellipsis)

        except ValueError:
            # No ellipsis.
            result = ( i for i in container if i in members )

        else:
            head, tail = container[: e], container[e + 1 :]
            assert Ellipsis not in tail
            head = tuple( i for i in head if i in members )
            tail = tuple( i for i in tail if i in members )
            result = (
                  head
                + tuple( i for i in members if i not in head and i not in tail )
                + tail
            )

    elif isinstance(container, slice):
        result = tuple(items)[container]

    else:
        result = ( i for i in items if i in container )

    return ctor(result)


#-------------------------------------------------------------------------------

class Container:

    def __invert__(self):
        return _Not(self)


    def __and___(self, other):
        return _And(self, other)


    def __rand__(self, other):
        return self.__and__(other)


    def __or__(self, other):
        return _Or(self, other)


    def __ror__(self, other):
        return self.__or__(other)



#-------------------------------------------------------------------------------

class _All(Container):
    """
    Contains all itmes.
    """

    def __contains__(self, item):
        return True


    def __repr__(self):
        return "All"


    def __invert__(self):
        return {}


    def __and__(self, other):
        return other if is_container(other) else NotImplemented


    def __or__(self, other):
        return self if is_container(other) else NotImplemented



All = _All()

#-------------------------------------------------------------------------------

class _Not(Container):

    def __init__(self, container):
        self.__container = container


    def __repr__(self):
        return f"~{self.__container!r}"


    def __contains__(self, item):
        return item not in self.__container


    def __invert__(self):
        return self.__container



class _And(Container):

    def __init__(self, *containers):
        self.__containers = containers


    def __repr__(self):
        return " & ".join( repr(c) for c in self.__containers )


    def __contains__(self, item):
        return all( item in c for c in self.__containers )


    def __and__(self, other):
        return type(self)(self.__containers + (other, ))



class _Or(Container):

    def __init__(self, *containers):
        self.__containers = containers


    def __repr__(self):
        return " | ".join( repr(c) for c in self.__containers )


    def __contains__(self, item):
        return any( item in c for c in self.__containers )


    def __or__(self, other):
        return type(self)(self.__containers + (other, ))



#-------------------------------------------------------------------------------

class only(Container):
    """
    Contains only particular items.
    """

    def __init__(self, *items):
        self.__items = frozenset(items)


    def __repr__(self):
        return py.format_ctor(self, *self.__items)


    def __contains__(self, item):
        return item in self.__items



all_but = lambda *i: ~only(*i)

#-------------------------------------------------------------------------------

class regex:
    """
    Contains an item iff. its `str` matches a regular expression.
    """

    def __init__(self, regex):
        self.__regex = re.compile(regex)


    def __contains__(self, item):
        return self.__regex.match(str(item)) is not None



