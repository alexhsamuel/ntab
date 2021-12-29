try:
    from fixfmt import pad, elide, palide
except ImportError:
    from ._text import pad, elide, palide

def join_lines(lines):
    return "\n".join(lines) + "\n"



