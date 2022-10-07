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
pip install "blik[all]"
```

The `[all]` qualifier also installs `pyqt5` as the napari GUI backend, and a few additional napari plugins that you might find useful in your workflow:
- [napari-properties-plotter](https://github.com/brisvag/napari-properties-plotter)
- [napari-properties-viewer](https://github.com/kevinyamauchi/napari-properties-viewer)
- [napari-label-interpolator](https://github.com/kevinyamauchi/napari-label-interpolator)

## Basic Usage

From the command line:
```bash
napari -w blik -- /path/to.star /path/to/mrc/files/*
```

The `-w blik` is important for proper initialization of all the layers. Keep the main widget open to ensure nothing goes wrong!

*`blik` is just `napari`*. Particles and images are exposed as simple napari layers, which can be analysed and manipulated with simple python, and most importantly other [napari plugins](https://napari-hub.org/).

## Widget

The main widget has a few functions:
