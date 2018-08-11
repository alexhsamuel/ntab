try:
    from fixfmt import pad, elide, palide
except ImportError:
    from ._text import pad, elide, palide

__all__ = (
    "pad", 
    "elide", 
    "palide",
)

