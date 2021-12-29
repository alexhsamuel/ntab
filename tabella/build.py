import numpy as np

from   .table import Table

#-------------------------------------------------------------------------------

def from_array(array, Table=Table):
    """
    Contructs a table from a structured array or recarray.
    """
    return Table( (n, array[n]) for n in array.dtype.names )


def from_dataframe(df, Table=Table):
    """
    Constructs a table from a `pandas.DataFrame`.
    """
    return Table( (n, df[n].values) for n in df.names )


def from_recs(recs, Table=Table):
    """
    Constructs a table from an array of mapping records.

    All mappings must have the same keys.
    """
    # FIXME: There are much faster implementations for this.
    recs = iter(recs)
    cols = { n: [v] for n, v in next(recs).items() }
    for rec in recs:
        for n, v in rec.items():
            cols[n].append(v)
    return Table( (n, np.array(v)) for n, v in cols.items() )


def from_row_seqs(names, rows, *, dtypes={}) -> Table:
    """
    Constructs a table from an iterable of sequences.
    """
    # FIXME: Do better with type conversions.
    cols = [ [] for n in names ]
    for row in rows:
        for col, val in zip(cols, row):
            col.append(val)
    return Table({ n: np.array(c) for n, c in zip(names, cols) })


