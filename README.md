![logo](docs/images/logo.png)

# Blik

![Codecov branch](https://img.shields.io/codecov/c/github/gutsche-lab/blik/master?label=codecov)
![PyPI](https://img.shields.io/pypi/v/blik)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/blik)

*it means glance in Dutch*

**Blik** is a python tool for visualising and interacting with cryo-ET and subtomogram averaging data. It leverages the fast, multi-dimensional [napari viewer](https://napari.org) and the scientific python stack.

**DISCLAIMER**: this package is in early development phase. Expect frequent bugs and crashes. Please, report them on the issue tracker and ask if anything is unclear!

## Installation

```bash
pip install blik
```

## Basic Usage

From the command line:
```bash
blik /path/to.star /path/to/mrc/files/
```

Blik accepts any combination of files and directory, and will try find the right files and display them in napari. `blik` will also start an ipython shell with the following setup:
```python
import blik
dataset = DataSet([your_data])
viewer = dataset.napari_viewer
```

For more information, check out the help page with `blik -h` and [head over to the docs](https://gutsche-lab.github.io/blik).
