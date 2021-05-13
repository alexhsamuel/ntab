import functools

#-------------------------------------------------------------------------------

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


