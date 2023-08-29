![logo](https://github.com/brisvag/blik/raw/main/docs/images/logo.png)

# blik

[![License](https://img.shields.io/pypi/l/blik.svg?color=green)](https://github.com/brisvag/blik/raw/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/blik.svg?color=green)](https://pypi.org/project/blik)
[![Python Version](https://img.shields.io/pypi/pyversions/blik.svg?color=green)](https://python.org)
[![CI](https://github.com/brisvag/blik/actions/workflows/ci.yml/badge.svg)](https://github.com/brisvag/blik/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/brisvag/blik/branch/main/graph/badge.svg)](https://codecov.io/gh/brisvag/blik)

![blik showcase](https://user-images.githubusercontent.com/23482191/161224963-ad746a06-c2e5-46fe-a13b-f356bc4ad72b.png)

**`blik`** is a tool for visualising and interacting with cryo-ET and subtomogram averaging data. It leverages the fast, multi-dimensional [napari viewer](https://napari.org) and the scientific python stack.

**DISCLAIMER**: this package is in development phase. Expect bugs and crashes. Please, report them on the issue tracker and ask if anything is unclear!

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

- `experiment`: quickly switch to a different experiment id (typically, everything related to an individual tomogram such as volume, particles and segmentations)
- `new`: generate a new `segmentation`, a new manually-picked set of `particles`, or a new `surface picking` for segmentation or particle generation
- `add to exp`: add a layer to the currently selected `experiment` (just a shorthand for `layer.metadata['experiment_id'] = current_exp_id`)
- `surface`: process a previously picked `surface picking` layer to generate a surface mesh or distribute particles on it for subtomogram averaging.
