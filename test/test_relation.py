import numpy as np

from   tabela.relation import index
from   tabela.series import Series
from   tabela.table import Table, Row

#-------------------------------------------------------------------------------

def get_relation():
    tbl = Table({
        "num"   : [  3,   6,      2,       1,     8,   2,    0,    6],
        "name"  : ["c", "c",    "d",     "f",   "q", "a", "d", "foo"],
        "val"   : [  0,  -1, np.nan, 3.14159, 2.718, 100,   0,  1e-6],
        "data"  : np.arange(8) ** 2 + 1,
    })
    return index(tbl, ["name", "num"])


def test_repr():
    repr(get_relation())


def test_str():
    str(get_relation())


def test_cols():
    rln = get_relation()
    assert len(rln.cols) == 4
    assert tuple(rln.cols) == ("num", "name", "val", "data")
    assert tuple(rln.cols.keys()) == ("num", "name", "val", "data")
    for name, srs in rln.cols.items():
        print(name)
        assert isinstance(srs, Series)
        assert srs.index is rln.index
        assert list(srs.index.rows.values()) == list(range(8))
        assert isinstance(srs.col, np.ndarray)
        assert srs.col.shape == (8, )


def test_cols_dtypes():
    rln = get_relation()
    assert dict(rln.cols.dtypes) == {
        "num": int,
        "name": "<U3",
        "val": "float",
        "data": int,
    }


def test_rows():
    rln = get_relation()
    assert len(rln.rows) == 8
    keys = list(rln.rows)
    assert len(keys) == 8
    assert keys[1] == ("c", 6)
    keys = rln.rows.keys()
    assert list(keys)[-1] == ("foo", 6)
    assert next(iter(rln.rows.items()))[0] == ("c", 3)


def test_row_subscript():
    rln = get_relation()
    assert dict(rln.rows["c", 3]) == {"num": 3, "name": "c", "val": 0, "data": 1}
    assert rln.rows["d", 0]["val"] == 0
    row = rln.rows[("a", 2)]
    assert isinstance(row, Row)
    assert row["name"] == "a"
    assert row["data"] == 26


