import numpy as np
import random
import string

from   .tab import Table

#-------------------------------------------------------------------------------

def generate_symbols(num, num_syms):
    syms = frozenset(
        "".join( 
            random.choice(string.ascii_uppercase) 
            for _ in range(random.randint(1, 5))
        )
        for _ in range(num_syms)
    )
    return np.random.choice(tuple(syms), num)


def generate_table(*, num_rows=64) -> Table:
    arrs = {}
    arrs.update({
        f"idx{i}": np.cumsum(np.random.randint(1, 4, num_rows))
        for i in range(1)
    })
    arrs.update({
        f"val{i}": np.random.normal(1, 1, num_rows)
        for i in range(1)
    })
    arrs.update({
        f"sym{i}": generate_symbols(num_rows, 10)
        for i in range(1)
    })
    return Table(arrs)


