![logo](docs/images/logo.png)

# `blik`

![Codecov branch](https://img.shields.io/codecov/c/github/gutsche-lab/blik/master?label=codecov)
![PyPI](https://img.shields.io/pypi/v/blik)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/blik)

*it means glance in Dutch*

**`blik`** is a python tool for visualising and interacting with cryo-ET and subtomogram averaging data. It leverages the fast, multi-dimensional [napari viewer](https://napari.org) and the scientific python stack.

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

`blik` accepts any combination of files and directory, and will try find the right files and display them in napari. `blik` will also start an ipython shell with the following setup:
```python
import blik
dataset = DataSet([your_data])
viewer = dataset.napari_viewer
```

For more information, check out the help page with `blik -h` and [head over to the docs](https://gutsche-lab.github.io/blik).

## `napari` integration

*`blik` is just `napari`*. Particles and images are exposed as simple napari layers, which can be analysed and manipulated with simple python, and most importantly [napari plugins](https://napari-hub.org/).

### Property plotting

Particles loaded from a star file or similar format will contain all the additional data that comes in additional columns. To plot this data and select particles based on it, check out [napari-property-plotter](https://github.com/brisvag/napari-properties-plotter).
