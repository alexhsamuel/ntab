import functools

NO_DEFAULT = object()

#-------------------------------------------------------------------------------

def is_str(obj):
    return isinstance(obj, (str, bytes))


def iterize(obj):
    """
    Converts into or wraps in an iterator.

    If `obj` is an iterable object other than a `str`, returns an iterator.
    Otherwise, returns a one-element iterable of `obj`.

      >>> list(iterize((1, 2, 3)))
      [1, 2, 3]

      >>> list(iterize("Hello!"))
      ['Hello!']
      >>> list(iterize(42))
      [42]

    """
    if is_str(obj):
        return iter((obj, ))
    else:
        try:
            return iter(obj)
        except TypeError:
            return iter((obj, ))


def tupleize(obj):
    """
    Converts into or wraps in a tuple.

    If `obj` is an iterable object other than a `str`, converts it to a `tuple`.
      >>> tupleize((1, 2, 3))
      (1, 2, 3)
      >>> tupleize([1, 2, 3])
      (1, 2, 3)
      >>> tupleize(range(1, 4))
      (1, 2, 3)

    Otherwise, wraps `obj` in a one-element `tuple`.
      >>> tupleize(42)
      (42,)
      >>> tupleize(None)
      (None,)
      >>> tupleize("Hello, world!")
      ('Hello, world!',)

    """
    if is_str(obj):
        return (obj, )
    else:
        try:
            return tuple(obj)
        except:
            return (obj, )


def format_call(__name, *args, **kw_args):
    """
    Formats a function call as a string.  (Does not call any function.)

      >>> import math
      >>> format_call(math.hypot, 3, 4)
      'hypot(3, 4)'

      >>> format_call("myfunc", "arg", foo=42, bar=None)
      "myfunc('arg', foo=42, bar=None)"

    @param __name
      The name of the function, or the function itself.
    """
    name = __name.__name__ if hasattr(__name, "__name__") else str(__name)
    args = [ repr(a) for a in args ]
    args.extend( n + "=" + repr(v) for n, v in kw_args.items() )
    return name + "(" + ", ".join(args) + ")"


def format_ctor(obj, *args, **kw_args):
    """
    Formats an object construction as a string.

    Like `format_call`, but uses the type name of `obj` as the function name.

    Useful for quick-and-dirty `__repr__` implementations:

      >>> class C:
      ...     def __init__(self, foo):
      ...         self.foo = foo
      ...     def __repr__(self):
      ...         return format_ctor(self, foo=self.foo)
      ... 
      >>> C(42)
      C(foo=42)

    """
    return format_call(obj.__class__, *args, **kw_args)


def sort_as(items, order):
    items = list(items)
    # First generate items from `order`, as long as they appear in `items`.
    for item in order:
        try:
            i = items.index(item)
        except ValueError:
            pass
        else:
            yield item
            del items[i]
    # Then, generate any remaining items from `items`.
    for item in items:
        yield item


def first_key(mapping):
    return next(iter(mapping))


def first_value(mapping):
    return next(iter(mapping.values()))


def first_item(mapping):
    return next(iter(mapping.items()))


def normalize_index(index, length):
    """
    Normalizes an index per sequence indexing.

      >>> normalize_index(0, 10)
      0
      >>> normalize_index(9, 10)
      9
      >>> normalize_index(-2, 10)
      8

    """
    index = int(index)
    if 0 <= index < length:
        return index
    elif -length <= index < 0:
        return index + length
    else:
        raise IndexError("index out of range: {}".format(index))


def all_equal(items, default=NO_DEFAULT):
    """
    If all `items` are equal, returns one of them.

    :raise ValueError:
      Not all `items` are equal.
    """
    def check(a, b):
        if not (a == b):
            raise ValueError("not equal")
        return a

    try:
        return functools.reduce(check, items)
    except TypeError:
        # No items.
        if default is NO_DEFAULT:
            raise TypeError("no items") from None
        else:
            return default


