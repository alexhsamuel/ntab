import numpy as np

#-------------------------------------------------------------------------------

def to_array(tab):
    """
    Converts the table to a NumPY recarray.
    """
    dtype = np.dtype([ (n, a.dtype) for n, a in tab.arrs.items() ])
    recarr = np.empty(tab.num_rows, dtype=dtype)
    for name, arr in tab.arrs.items():
        recarr[name][:] = arr
    return recarr.view(np.recarray)


def to_dataframe(tab):
    """
    Converts the table to a Pandas dataframe.
    """
    import pandas as pd
    return pd.DataFrame.from_items(tab.arrs.items())


