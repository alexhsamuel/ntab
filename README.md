[![Build Status](https://travis-ci.org/alexhsamuel/ntab.svg?branch=master)](https://travis-ci.org/alexhsamuel/ntab)

ntab is a lightweight data table, similar to but much simpler than a Pandas
dataframe.

Conceptually, an ntab `Table` is nothing more than an ordered mapping from
column names to numpy arrays, and provides convenience features:

- Convenience constructors and I/O functions.
- Nice formatting, as text and HTML.
- Relational-style operations.
- Filtering functions.
- Row objects and row-oriented operations.

Consider ntab if you don't need the full weight of Pandas, go back and forth to
numpy a lot, or can't afford unnecessary copies of your column data.


# Examples

```
>>> from ntab import Table
>>> tbl = Table(label=["foo", "bar", "baz", "bif"], value=[3, 4.5, -1, 6.2], count=[100, 14, 72, 196])
>>> print(tbl)
label value count
----- ----- -----
foo     3.0   100
bar     4.5    14
baz    -1.0    72
bif     6.2   196

>>> tbl.a.value
array([ 3. ,  4.5, -1. ,  6.2])
>>> tbl.rows[2]
Row(2, label='baz', value=-1.0, count=72)
```


# Installing

From master:

```
pip install git+https://github.com/alexhsamuel/ntab
```

To hack on ntab, simply place your clone directory into your `PYTHONPATH`.

