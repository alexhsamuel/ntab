from   __future__ import absolute_import, division, print_function, unicode_literals

from   ntab import Table, GroupBy

#-------------------------------------------------------------------------------

def test_basic_1():
    tbl = Table(
        sym=["foo", "bar", "foo", "foo", "bar", "foo", ],
        val=[    3,     7,     8,     4,     1,     9, ],
    )
    grp = GroupBy(tbl, "sym")
    assert len(grp) == 2
    assert list(grp.keys()) == ["bar", "foo"]

    foo = grp["foo"]
    assert foo.num_cols == 2
    assert sorted(foo.names) == ["sym", "val"]
    assert foo.num_rows == 4
    assert (foo.a.sym == "foo").all()
    assert list(foo.a.val) == [3, 8, 4, 9]

    bar = grp["bar"]
    assert bar.num_cols == 2
    assert sorted(bar.names) == ["sym", "val"]
    assert bar.num_rows == 2
    assert (bar.a.sym == "bar").all()
    assert list(bar.a.val) == [7, 1]


def test_agg_0():
    tbl = Table(
        sym=["foo", "bar", "foo", "foo", "bar", "foo", ],
        val=[    3,     7,     8,     4,     1,     9, ],
    )

    grp = GroupBy(tbl, "sym")
    assert list(grp.counts()) == [2, 4]

    val = grp.agg.val
    assert list(val.sum()) == [ 8, 24]
    assert list(val.min()) == [ 1,  3]
    assert list(val.max()) == [ 7,  9]
    assert list(val(lambda a: a[ 0])) == [7, 3]
    assert list(val(lambda a: a[-1])) == [1, 9]


