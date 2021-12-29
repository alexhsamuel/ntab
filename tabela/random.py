from   functools import partial
import numpy as np

from   .lib.py import tupleize
from   .table import Table

#-------------------------------------------------------------------------------

def cumsum(gen):
    return lambda n: gen(n).cumsum()


def normal(mu=0, sigma=1):
    return partial(np.random.normal, mu, sigma)


def uniform(lo=0, hi=1):
    return partial(np.random.uniform, lo, hi)


def uniform_int(lo, hi):
    return partial(np.random.randint, lo, hi + 1)


def token(length, upper=False):
    """
    Returns a generator for random alphabetic tokens.

    :param length:
      Fixed string length, or a random function to generate it.
    :param upper:
      If true, use capital A-Z; else use lower-case a-z.
    """
    def gen(shape):
        if callable(length):
            lengths = length(shape)
            field_length = lengths.max()
        else:
            field_length = int(length)

        # Random words of field_length.
        result = np.random.randint(
            ord("A" if upper else "a"),
            ord("Z" if upper else "z") + 1,
            tupleize(shape) + (field_length, ),
            dtype="uint32"
        )

        if callable(length):
            # Truncate each to the desired length.
            result[
                np.broadcast_to(np.arange(field_length), result.shape)
                > lengths[..., np.newaxis]
            ] = 0

        return result.view(("U", field_length))[..., 0]

    return gen


def choice(choices):
    return partial(np.random.choice, choices)


def table(**kw_args):
    def gen(length):
        return Table({ n: g(length) for n, g in kw_args.items() })

    return gen


DEMO = table(**{
    "name0": token(4, upper=True),
    "name1": token(6, upper=True),
    "val0" : uniform_int(0,  9),
    "val1" : uniform_int(0, 19),
    "data" : normal(0, 1),
})


