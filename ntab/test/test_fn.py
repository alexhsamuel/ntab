from   ntab import Table, fn
from   ntab.lib.container import ALL, all_but

#-------------------------------------------------------------------------------

def test_select_arrs():
    tab = Table(x=[3,4,5], y=[4,5,6], z=[5,6,7], w=[6,7,8])
    assert tab.names == ["x", "y", "z", "w"]

    sel = fn.select_arrs(tab, ALL)
    assert sel.names == ["x", "y", "z", "w"]

    sel = fn.select_arrs(tab, all_but("y"))
    assert sel.names == ["x", "z", "w"]

    sel = fn.select_arrs(tab, ("w", "z"))
    assert sel.names == ["w", "z"]


def test_get_const_empty():
    tab = Table()
    assert tab.num_rows == 0
    assert fn.get_const(tab) == {}
    assert fn.remove_const(tab) == {}


def test_get_const_one():
    tab = Table(x=[3], y=[4.25], z=["Hello."])
    assert fn.get_const(tab) == dict(x=3, y=4.25, z="Hello.")


def test_get_const():
    tab = Table(
        x=[3, 4, 5, 6],
        y=[4, 4, 4, 4],
        z=[4.25, 4.26, 4.27, 4.28],
        w=[4.27, 4.27, 4.27, 4.27],
        u=["hello", "hello", "world", "hello"],
        v=["hello", "hello", "hello", "hello"],
    )
    assert tab.num_cols == 6
    assert tab.num_rows == 4
    assert fn.get_const(tab) == {"y": 4, "w": 4.27, "v": "hello"}
    assert fn.remove_const(tab) == {"y": 4, "w": 4.27, "v": "hello"}
    assert set(tab.arrs) == {"x", "z", "u"}


