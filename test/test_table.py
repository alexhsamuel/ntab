import numpy as np
from   numpy.testing import assert_array_equal as arr_eq
import pytest

from   tabela.table import Table, collect, col_fn
from   tabela.lib.container import all_but

#-------------------------------------------------------------------------------

def get_table():
    return Table({
        "num"   : [  3,   6,      2,       1,     8,   2,    0,    6],
        "name"  : ["c", "c",    "d",     "f",   "q", "a", "d", "foo"],
        "val"   : [  0,  -1, np.nan, 3.14159, 2.718, 100,   0,  1e-6],
    })


def test_repr():
    repr(get_table())


def test_str():
    str(get_table())


def test_cols():
    tbl = get_table()
    assert len(tbl.cols) == 3
    assert tuple(tbl.cols) == ("num", "name", "val")
    assert tuple(tbl.cols.keys()) == ("num", "name", "val")
    for name, arr in tbl.cols.items():
        print(name)
        assert isinstance(arr, np.ndarray)
        assert arr.shape == (8, )
    a = tbl.cols["num"]
    assert a.dtype == int
    assert a[0] == 3
    a = tbl.cols["name"]
    assert a.dtype.kind == "U"
    assert a[-1] == "foo"
    a = tbl.cols["val"]
    assert a[3] == 3.14159


def test_rows():
    tbl = get_table()
    assert len(tbl.rows) == 8
    rows = list(tbl.rows)
    assert len(rows) == 8

    row = tbl.rows[1]
    str(row)
    repr(row)
    assert row.__idx__ == 1
    assert len(row) == 3
    assert tuple(row) == ("num", "name", "val")
    assert tuple(row.keys()) == ("num", "name", "val")
    assert tuple(row.values()) == (6, "c", -1)
    assert row["name"] == "c"
    assert row["val"] == -1

    row = tbl.rows[-1]
    str(row)
    repr(row)
    assert row.__idx__ == 7
    assert len(row) == 3
    assert tuple(row) == ("num", "name", "val")
    assert tuple(row.keys()) == ("num", "name", "val")
    assert tuple(row.values()) == (6, "foo", 1e-6)
    assert row["name"] == "foo"
    assert row["val"] == 1e-6


def test_cols_dtypes():
    tbl = get_table()
    assert dict(tbl.cols.dtypes) == {"num": int, "name": "<U3", "val": float}


def test_col_fn():
    t = Table({
        "x": [3, 4, 5, 6],
        "y": [100, 100, 200, 200],
        "z": ["foo", "bar", "baz", "bif"],
    })

    @col_fn()
    def add_up(x, y):
        return collect(
            total   =x + y,
            y       =y // 100,
        )

    res = add_up(t)
    assert list(res.cols) == ["total", "y"]
    arr_eq(res.cols["total"], [103, 104, 205, 206])
    arr_eq(res.cols["y"], [1, 1, 2, 2])

    res = add_up(t, x=[5, 6, 7, 8])
    arr_eq(res.cols["total"], [105, 106, 207, 208])

    with pytest.raises(TypeError):
        # Col "z" doesn't match a param.
        add_up(t, strict=True)


def test_col_select():
    t = get_table()

    r = t.cols.select["name", "num", "val"]
    assert tuple(r.cols) == ("name", "num", "val")

    r = t.cols.select[("val", "name")]
    assert tuple(r.cols) == ("val", "name")

    r = t.cols.select["num"]
    assert tuple(r.cols) == ("num", )

    r = t.cols.select[1 :]
    assert tuple(r.cols) == ("name", "val")

    r = t.cols.select[:: -1]
    assert tuple(r.cols) == ("val", "name", "num")

    r = t.cols.select["name", ...]
    assert tuple(r.cols) == ("name", "num", "val")

    r = t.cols.select["val", ..., "num"]
    assert tuple(r.cols) == ("val", "name", "num")

    r = t.cols.select[..., "num"]
    assert tuple(r.cols) == ("name", "val", "num")

    r = t.cols.select[all_but("val")]
    assert tuple(r.cols) == ("num", "name")

    # FIXME: Test errors.


