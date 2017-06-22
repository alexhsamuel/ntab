from   __future__ import absolute_import, division, print_function, unicode_literals

import six

from   .lib.text import palide

#-------------------------------------------------------------------------------

def format_row(row, width=80, max_name_width=32):
    """
    @rtype
      Generator of lines.
    """
    vals = row.__dict__
    name_width = min(max_name_width, max( len(n) for n in vals ))
    for name, val in six.iteritems(vals):
        yield "{}: {}".format(
            palide(name, name_width),
            palide(str(val), width - name_width - 2)
        )


