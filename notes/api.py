t = load_csv_file("data.csv")

row = t.rows[0]

b = t.by("ticker", "expiry", "strike", "call_put")  # checks uniqueness?
row = b["AAPL", Date(2020, 1, 31), 307.5, "C"]

b.rels["price"]

b1 = b["AAPL", Date(2020, 1, 31)]

g = t.group_by("ticker", "expiry")

Table.cols[name] -> Array
Table.rows[n] -> Row

Table.by() -> IndexedTable  # checks uniqueness

IndexedTable.cols[name] -> Relation
IndexedTable.rows[key] -> Row

#-------------------------------------------------------------------------------

alias Key = Sequence
alias Value = Any
alias Name = str
alias Row = Mapping[Name, Value]

# Table:

t.cols  # Mapping[Name, ndarray]
t.rows  # Sequence[Row]

# Relation:

r.cols  # Mapping[Name, Series]
r.rows  # Mapping[Key, Row]
r.index # Index

# Series

s       # Mapping[Key, Value]
s.index # Index
s.col   # ndarray

# Index:

i.cols  # Mapping[Name, ndarray]
i.rows  # Mapping[Key, int]



t = load_csv_file("data.csv")
r = t.index(("ticker", "expiry", "strike", "cp"))

# Todo:
# - rename Column to Array ?? maybe not

#-------------------------------------------------------------------------------

# NOTE:
#  c[a, b, c, ...] == c[(a, b, c, ...)] for len > 1

# Name slicing

t.col[name] -> ndarray
r.cols[name] -> Series

# Selection 
t.cols[name]  # → t.cols.get(name)
t.cols.get(name[, default])
t.cols.get(idx[, default])

# Slicing
t.cols.select(slice(None, -2))
t.cols.select[...]  # → t.cols.select(...)
# The slice may be:

# Numerical slices:
t.cols.select[:: -1]  # etc
# How about by name?
t.cols.select[name0 : name1]

# Container selection:
t.cols.select[name]  # one item slice
# Containers:
t.cols.select[all_but(name)]
t.cols.select[glob("foo*")]

# Selection by names or idxs:
t.cols.select[[name0, name1]]
t.cols.select[(name0, name1)]
t.cols.select[name0, name1]  # same as previous
# Ellipsis
t.cols.select[name0, ..., name1]  # reorder
   # → t.cols.select((name0, Ellipsis, name1))

#-------------------------------------------------------------------------------

# Key slicing

s[Key] -> Value
s[slice] -> Series

r.rows.get((val0, val1), default)
r.rows[val0, val1] = r.rows[(val0, val1)]  # → r.rows.get((val0, val1))

r.rows(val0, name1=val1)  # mix of args and kw_args

r.rows.select(val0, val1)
r.rows.select(name0=val0, name1=val1)

r.rows.select[val0, slice1]  # → r.rows.select(val0, slice1)

r.rows.select([val0, val1, val2], ...)
r.rows.select(all_but(val), ...)
# etc

r.rows.mask(mask)

r.rows.select[(3, 4)] == r.rows[3, 4]
r.rows.select[(3, )] != r.rows[3]
# instead
r.rows.select[(3, 4), :]


# One index col:
r.rows.select[3]            → 3
r.rows.select[(3, )]        → (3, )
r.rows.select[(3, ), ]      → ((3, ), )
r.rows.select[3, 4, 5]      → (3, 4, 5)  # err
r.rows.select[(3, 4, 5)]    → (3, 4, 5)  # err
r.rows.select[(3, 4, 5), ]  → ((3, 4, 5), )

# Three index cols:
r.rows.select[3, 4, 5]      → (3, 4, 5)
r.rows.select[(3, 4, 5)]    → (3, 4, 5)

    def __getitem__(self, key):
        if not isinstance(key, tuple):
            key = (key, )
        try:
            e = key.index(Ellipsis)
        except ValueError:
            # Found ellipsis. There shouldn't be another.
            assert Ellipsis not in key[e + 1 :]
            # Replace ellipsis with the right number of null slices.
            key = key[: e] + (slice(None), ) * (len(cols) - (len(key) - 1)) + key[e + 1 :]
        else:
            assert len(key) == len(cols) or Ellipsis in key


#===============================================================================

@col_fn()
def add_up(x, y):
    return collect(total=x + y, y=y // 100)

res = add_up(t)
res = add_up(t, x=[5, 6, 7, 8])

#--- vs

def add_up(t):
    x, y = unpack_cols(t, "x", "y")
    return collect(total=x + y, y=y // 100)


res = add_up(t)
res = add_up(t.cols.setting(x=[5, 6, 7, 8]))

#--- vs

# Not as good.

def add_up(x, y):
    return collect(total=x + y, y=y // 100)

res = add_up(**t.cols)  # always strict
res = add_up(x=[5, 6, 7, 8], **t.cols)  # doesn't work due to double x

#--- vs this horrific nonsense

# SEE THIS: https://faster-cpython.readthedocs.io/mutable.html#local-variables

with local_cols(t):
    total = x + y
    y //= 100


#-------------------------------------------------------------------------------

# How should we spell non-mutating column assignment?

t.cols.set(x=[...])
t.cols.setting(x=[...])
t.cols.add(x=[...])
t.cols.assign(x=[...])
t.cols.having(x=[...])
t.cols.with_(x=[...])
t.cols |= dict(x=[...])
