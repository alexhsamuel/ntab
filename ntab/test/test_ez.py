from   __future__ import absolute_import, division, print_function, unicode_literals

from   ntab import Table, ez

#-------------------------------------------------------------------------------

def test_vars():
    tab = Table(x=[3, 4, 5, 6], y=[4, 5, 6, 7])

    with ez.vars(tab):
        total = x.sum() + y.sum()

    assert total == 40

    assert "x" not in locals()
    assert "y" not in locals()


def test_vars_add_cols():
    tab = Table(x=[3, 4, 5, 6], y=[4, 5, 6, 7])

    with ez.vars(tab, add_cols=False):
        s = x + y
        d = y - x

    assert list(s) == [ 7,  9, 11, 13]
    assert list(d) == [ 1,  1,  1,  1]



def test_vars_no_add_cols():
    tab = Table(x=[3, 4, 5, 6], y=[4, 5, 6, 7])

    with ez.vars(tab, add_cols=False):
        s = x + y
        d = y - x

    assert sorted(tab.arrs) == ["x", "y"]



