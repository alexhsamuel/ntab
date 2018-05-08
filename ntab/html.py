from   __future__ import absolute_import, division, print_function, unicode_literals

from   cgi import escape
import functools
import traceback

from  .lib.text import elide

#-------------------------------------------------------------------------------

CSS = """
.tab-exception {
  padding: 4px;
  background-color: 0xfff0f0;
}

.tab-table {
  line-height: 60%;
}

.tab-table thead {
  line-height: 120%;
}

.tab-table td, .tab-table th, .tab-table tr {
}

.tab-table tbody {
  font-family: Consolas, monospace;
  font-size: 85%;
}

.tab-table tbody tr:nth-child(odd) {
  background: #f8f8f8;
}

table.tab-table {
  border-collapse: collapse;
  border: none;
}

.tab-row {
  line-height: 60%;
}

.tab-row th {
  font-size: 85%;
  border-right: 1px solid #c0c0c0;
}

.tab-row td {
  font-family: Consolas, monospace;
  font-size: 85%;
}
"""

#-------------------------------------------------------------------------------

def format_exc(fn):
    """
    Wraps a function to format exceptions as HTML.

    Jupyter silently ignores exceptions raised from formatters, which is really
    confusing.  With this wrapper, we catch and format them.
    """
    @functools.wraps(fn)
    def wrapped(*args, **kw_args):
        try:
            return fn(*args, **kw_args)
        except:
            return """
                <div class="tab-exception">
                  <b>exception in <code>Table._repr_html_</code>:</b>
                  <pre>{}</pre>
                </div>
            """.format(escape(traceback.format_exc()))

    return wrapped


def _render(table, css_class="tab-table", max_rows=None):
    names   = list(table.arrs.keys())
    arrs    = list(table.arrs.values())
    if max_rows is not None:
        arrs = [ a[: max_rows] for a in arrs ]
    aligns  = [
        "left" if a.dtype.kind in {"U", "S", "b"} else "right"
        for a in arrs
    ]

    arrs = [ [ str(v) for v in a ] for a in arrs ]
    widths = [ 
        0 if table.num_rows == 0 else max( len(v) for v in a ) 
        for a in arrs 
    ]

    yield "<style>\n" + CSS + "</style>"
    yield "<table class='{}'>".format(escape(css_class))
    yield "<thead>"
    yield "<tr>"
    for name, width in zip(names, widths):
        yield "<th>{}</th>".format(elide(name, max(width, 8), pos=0.7))
    yield "</tr>"
    yield "</thead>"
    yield "<tbody>"
    if table.num_rows == 0:
        yield "<tr>"
        yield "<td colspan='{}' style='text-align: center'>... empty ...</td>".format(len(names))
        yield "</tr>"
    else:
        for row in zip(*arrs):
            yield "<tr>"
            for val, align in zip(row, aligns):
                if isinstance(val, str):
                    val = val.encode("string_escape")
                yield "<td style='text-align: {};'>{}</td>".format(
                    align, escape(val))
            yield "</tr>"
    if max_rows is not None and max_rows < table.num_rows:
        yield "<tfoot>"
        yield "<tr>"
        yield "<td colspan='{}' style='text-align: center'>... {} rows total ...</td>".format(
            len(names), table.num_rows)
        yield "</tr>"
        yield "</tfoot>"
    yield "</tbody>"
    yield "</table>"



def render(table, max_rows=None):
    """
    Renders the table as an HTML table element.

    @param max_rows
      Maximum number of rows to show.
    @return
      HTML rendering of the table.
    """
    return "".join(_render(table, max_rows=max_rows))


#-------------------------------------------------------------------------------

def _render_row(row, css_class="tab-row"):
    vals = row.__dict__

    yield "<style>\n" + CSS + "</style>"
    yield "<table class='{}'>".format(escape(css_class))
    yield "<thead><tr><th>idx</th><td>{}</td></tr></thead>".format(row.__idx__)
    yield "<tbody>"
    for name, val in vals.items():
        yield "<tr>"
        yield "<th>{}</th>".format(escape(name))
        yield "<td>{}</td>".format(escape(str(val)))
        yield "</tr>"
    yield "</tbody>"
    yield "</table>"


def render_row(row):
    """
    Renders a row as an HTML table element.
    """
    return "".join(_render_row(row))


