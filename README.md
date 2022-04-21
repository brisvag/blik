![logo](https://github.com/gutsche-lab/blik/raw/main/docs/images/logo.png)

# `blik`

![Codecov branch](https://img.shields.io/codecov/c/github/gutsche-lab/blik/main?label=codecov)
![PyPI](https://img.shields.io/pypi/v/blik)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/blik)

*it means glance in Dutch*

![blik showcase](https://user-images.githubusercontent.com/23482191/161224963-ad746a06-c2e5-46fe-a13b-f356bc4ad72b.png)

**`blik`** is a tool for visualising and interacting with cryo-ET and subtomogram averaging data. It leverages the fast, multi-dimensional [napari viewer](https://napari.org) and the scientific python stack.

**DISCLAIMER**: this package is in development phase. Expect frequent bugs and crashes. Please, report them on the issue tracker and ask if anything is unclear!

## Installation

You can either install `blik` through the [napari plugin system](https://napari.org/plugins/index.html), through pip, or get both napari and blik directly with:

```bash
pip install blik[all]
```

## Basic Usage

From the command line:
```bash
napari /path/to.star /path/to/mrc/files/* [-w blik]
```

The optional `-w blik` addition will open the main blik widget and set up a few things (such as the scale bar) on the napari viewer.

*`blik` is just `napari`*. Particles and images are exposed as simple napari layers, which can be analysed and manipulated with simple python, and most importantly other [napari plugins](https://napari-hub.org/).
