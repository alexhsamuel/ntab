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

def format_arrs(arrs, *, max_length=32, header=True, num_index=0):
    """
    :param arrs:
      Iterable of name, arr pairs.
    :param num_index:
      Number of leading items in `arrs` to format as index.
    """
    names, arrs = zip(*arrs)
    num_rows = len(arrs[0])

    if fixfmt is None:
        def fmt(val):
            if isinstance(val, np.ndarray):
                return " ".join( str(a) for a in val )
            else:
                return str(val)

        num_rows = max(max_length, num_rows)

        # Format all values.
        fmted = [ [ fmt(v) for v in a ] for a in arrs.values() ]
        # Find widths.
        if num_rows == 0:
            widths = [0] * len(names)
        else:
            widths = [ max( len(v) for v in c ) for c in fmted ]
        if header:
            widths = [ max(len(n), w) for n, w in zip(names, widths) ]
        justs = [False] * len(names)

        if max_length is not None:
            fmted = [ a[: max_length] for a in fmted ]
        rows = ( 
            " ".join( pad(v, w) for v, w in zip(r, widths) ) 
            for r in zip(*fmted) 
        )

    else:
        # FIXME: From col.
        fmts = [ 
            fixfmt.npfmt.choose_formatter(a, min_width=min(6, len(n)))
            for n, a in zip(names, arrs)
        ]
        widths = [ f.width for f in fmts ]
        justs = [ isinstance(f, fixfmt.Number) for f in fmts ]
        # FIXME: Use fixfmt.Table.
        rows = ( 
            " ".join( f(v) for f, v in zip(fmts, r) ) 
            for r in zip(*arrs) 
        )
        if max_length is not None:
            rows = itertools.islice(rows, max_length)

    # Header.
    yield " ".join( 
        palide(n, w, elide_pos=0.7, pad_pos=0 if j else 1)
        for n, w, j in zip(names, widths, justs)
    )
    yield " ".join(
        ("=" if i < num_index else "-") * w
        for i, w in enumerate(widths)
    )

    try:
        yield next(rows)
    except StopIteration:
        yield "... empty table ..."

    yield from rows

    total_width = sum( 1 + w for w in widths )
    if max_length is not None and max_length < num_rows:
        yield pad(
            "... {} rows total ...".format(num_rows), 
            total_width, pos=0.5)


def format_row(row, width=80, max_name_width=32):
    """
    @rtype
      Generator of lines.
    """
    name_width = min(max_name_width, max( len(n) for n in row ))
    for name, val in row.items():
        yield "{}: {}".format(
            palide(name, name_width),
            palide(str(val), width - name_width - 2)
        )


