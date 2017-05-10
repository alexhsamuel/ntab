import setuptools

setuptools.setup(
    name="ntab",
    version="0.0.0",
    description="Simple numerical tables",
    # long_description=long_description,
    url="https://github.com/alexhsamuel/ntab",
    author="Alex Samuel",
    author_email="alex@alexsamuel.net",
    license="MIT",
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 3 - Alpha",

        # Indicate who your project is intended for
        "Intended Audience :: Developers",
        # "Topic :: Software Development :: Build Tools",

        "License :: OSI Approved :: MIT License",

        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
    ],

    # What does your project relate to?
    keywords="table numerical",

    packages=setuptools.find_packages(exclude=[]),

    install_requires=[
        "future",
        "numpy",
        "six",
    ],

    package_data={},
    data_files=[],
    entry_points={},
)

