import numpy as np

from   .tab import Table

#-------------------------------------------------------------------------------

def random_str_arr(n, width, min=ord("A"), max=ord("Z")):
    return (
        np.random.randint(min, max + 1, n * width, "uint8")
        .view(("S", width))
        .astype(str)
    )


def make(n=128):
    return Table(
        i       =np.arange(n),
        j       =(np.arange(n) + 1) ** 3,
        u1      =np.random.random(n),
        u2      =np.round(np.random.random(n), 5),
        label   =random_str_arr(n, 8),
        big     =np.exp(np.random.random(n) * 20),
        code    =random_str_arr(n, 1),
        flag    =np.random.randint(0, 2, n).astype(bool),
        sym     =random_str_arr(12, 3)[np.random.randint(0, 12, n)],
    )


