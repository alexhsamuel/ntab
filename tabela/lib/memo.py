import functools

#-------------------------------------------------------------------------------

def memoize_with(memo):
    def memoize(fn):
        @functools.wraps(fn)
        def memoized(*args, **kw_args):
            # FIXME: It would be better to bind to the signature first, to pick
            # up default arguments.
            key = args + tuple(sorted(kw_args.items()))
            try:
                return memo[key]
            except KeyError:
                value = memo[key] = fn(*args, **kw_args)
                return value

        memoized.__memo__ = memo
        return memoized

    return memoize


def memoize(fn):
    """
    Memoizes with a new empty `dict`.
    """
    return memoize_with({})(fn)


def lazy_property(fn):
    name = fn.__name__

    @functools.wraps(fn)
    def wrapped(self):
        try:
            return self.__dict__[name]
        except KeyError:
            val = fn(self)
            self.__dict__[name] = val
            return val

    return property(wrapped)


