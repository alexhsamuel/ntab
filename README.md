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


# Installing

From master:

```
pip install git+https://github.com/alexhsamuel/ntab
```

To hack on ntab, simply place your clone directory into your `PYTHONPATH`.

