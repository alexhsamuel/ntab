```py
from serese import Table, group_by, align_to, align

def test():
    tbl = Table(
        sym=["foo", "bar", "foo", "foo", "bar", "foo", ],
        val=[    3,     7,     8,     4,     1,     9, ],
    )
    sym = tbl.arrs["sym"]
    val = tbl.arrs["val"]

    result = group_by(sym).reduce(sum)(val)


    sym = align_to(val, sym, fill=0)

    val, sym = align((val, sym), type="inner")

    tab = Table.from_cols({"sym": sym, "val": val})

    tids = options.arrs["tids"]

```

```py
r = Relation({"k": [1, 2, 3]}, [10, 20, 31])
assert r[2] == 20
```

