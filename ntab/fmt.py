from   __future__ import absolute_import, division, print_function, unicode_literals

import itertools
import numpy as np

from   .lib.text import pad, palide

# Use https://github.com/alexhsamuel/fixfmt if available.
try:
    import fixfmt
    import fixfmt.npfmt
except ImportError:
    fixfmt = None

#-------------------------------------------------------------------------------

def format_table(tbl, max_length=32, header=True):
    names = list(tbl.arrs.keys())

    if fixfmt is None:
        def fmt(val):
            if isinstance(val, np.ndarray):
                return " ".join( str(a) for a in val )
            else:
                return str(val)

        num_rows = max(max_length, tbl.num_rows)

        # Format all values.
        arrs = ( [ fmt(v) for v in a ] for a in tbl.arrs.values() )
        if max_length is not None:
            arrs = ( a[: max_length] for a in arrs )
        arrs = list(arrs)

        # Find widths.
        if num_rows == 0:
            widths = [0] * tbl.num_cols
        else:
            widths = [ max( len(v) for v in c ) for c in arrs ]
        if header:
            widths = [ max(len(n), w) for n, w in zip(names, widths) ]
        justs = [False] * tbl.num_cols
        rows = ( 
            " ".join( pad(v, w) for v, w in zip(r, widths) ) 
            for r in zip(*arrs) 
        )

    else:
        fmts = [ 
            fixfmt.npfmt.choose_formatter(a, min_width=min(6, len(n)))
            for n, a in tbl.arrs.items() 
        ]
        widths = [ f.width for f in fmts ]
        justs = [ isinstance(f, fixfmt.Number) for f in fmts ]
        rows = ( 
            " ".join( f(v) for f, v in zip(fmts, r) ) 
            for r in zip(*tbl.arrs.values()) 
        )
        if max_length is not None:
            rows = itertools.islice(rows, max_length)

    # Header.
    yield " ".join( 
        palide(n, w, elide_pos=0.7, pad_pos=0 if j else 1)
        for n, w, j in zip(names, widths, justs)
    )
    yield " ".join( "-" * w for w in widths )

    try:
        yield next(rows)
    except StopIteration:
        yield "... empty table ..."

    yield from rows

    total_width = sum( 1 + w for w in widths )
    if max_length is not None and max_length < tbl.num_rows:
        yield pad(
            "... {} rows total ...".format(tbl.num_rows), 
            total_width, pos=0.5)


def format_row(row, width=80, max_name_width=32):
    """
    @rtype
      Generator of lines.
    """
    vals = row.__dict__
    name_width = min(max_name_width, max( len(n) for n in vals ))
    for name, val in vals.items():
        yield "{}: {}".format(
            palide(name, name_width),
            palide(str(val), width - name_width - 2)
        )


