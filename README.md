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
- [napari-label-interpolator](https://github.com/brisvag/napari-label-interpolator)

### Nightly build

If you'd like the most up to date `blik` possible, you can install directly from the `main` branch on github. This also uses napari `main`, so expect some instability!

```
pip install "git+https://github.com/brisvag/blik.git@main#egg=blik[all]"
pip install "git+https://github.com/napari/napari.git@main#egg=napari[all]"
```

## Basic Usage

From the command line:
```bash
napari -w blik -- /path/to.star /path/to/mrc/files/*
```

The `-w blik` is important for proper initialization of all the layers. Always open the main widget open to ensure nothing goes wrong!

*`blik` is just `napari`*. Particles and images are exposed as simple napari layers, which can be analysed and manipulated with simple python, and most importantly other [napari plugins](https://napari-hub.org/).

## Widgets

The main widget has a few functions:

- `experiment`: quickly switch to a different experiment id (typically, everything related to an individual tomogram such as volume, particles and segmentations)
- `new`: generate a new `segmentation`, a new manually-picked set of `particles`, or a new `surface picking` or `filament picking` for segmentation, particle generation or volume resampling.
- `add to exp`: add a layer to the currently selected `experiment` (just a shorthand for `layer.metadata['experiment_id'] = current_exp_id`)
- `slice_thickness`: changes the slicing thickness in all dimensions in napari. Images will be averaged over that thickness, and all particles in the slice will be displayed.

There are also widgets for picking of both surfaces and filaments.

- `surface`: process a previously picked `surface picking` layer to generate a surface mesh and distribute particles on it for subtomogram averaging, or resample a tomogram along the surface.
- `filament`: process a previously picked `filament picking` layer to generate a filament and distribute particles on it for subtomogram averaging, or resample a tomogram along the filament.

# References

A paper preprint about `blik` is available on the bioRxiv: [https://doi.org/10.1101/2023.12.05.570263](https://doi.org/10.1101/2023.12.05.570263).
