import setuptools
from   Cython.Build import cythonize

#-------------------------------------------------------------------------------

long_description = """
A lightweight Python tabular data structure.

Collects parallel numpy arrays into a tabular data structure.  Provides
syntactic sugar for column- and row-wise access, and basic grouping and
aggregation.  Avoids copies and type conversions; does not mess around with the
underlying numpy arrays.  Much less functionality than Pandas, with many fewer
lines of code.
"""

setuptools.setup(
    name            ="ntab",
    version         ="0.4.0",
    description     ="Simple numerical tables",
    long_description=long_description,
    url             ="https://codeberg.org/alexhsamuel/ntab",
    author          ="Alex Samuel",
    author_email    ="alex@alexsamuel.net",
    license         ="MIT",
    keywords        =["data", "table", "numerical", "numpy"],
    classifiers     =[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
    ],

    extras_require={
        "dev": ["cython", "pytest"],
        "build": ["cython", ],
    },

    install_requires=[
        "numpy",
    ],

    packages        =setuptools.find_packages(exclude=[]),
    ext_modules     =cythonize("tabela/analyze.pyx"),
    package_data    ={"": ["test/*"]},
    data_files      =[],
    entry_points    ={},
)

