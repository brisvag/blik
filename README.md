![logo](https://github.com/brisvag/blik/raw/main/docs/images/logo.png)

# blik

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.10090438.svg)](https://zenodo.org/doi/10.5281/zenodo.10090438)
[![Paper DOI](https://zenodo.org/badge/DOI/10.1371/journal.pbio.3002447.svg)](https://doi.org/10.1371/journal.pbio.3002447)
[![License](https://img.shields.io/pypi/l/blik.svg?color=green)](https://github.com/brisvag/blik/raw/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/blik.svg?color=green)](https://pypi.org/project/blik)
[![Python Version](https://img.shields.io/pypi/pyversions/blik.svg?color=green)](https://python.org)
[![CI](https://github.com/brisvag/blik/actions/workflows/ci.yml/badge.svg)](https://github.com/brisvag/blik/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/brisvag/blik/branch/main/graph/badge.svg)](https://codecov.io/gh/brisvag/blik)


![blik showcase](https://private-user-images.githubusercontent.com/23482191/361246457-b7447060-7ccd-4a8c-a41c-55c1678bf089.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3MjQ2MDQ0OTksIm5iZiI6MTcyNDYwNDE5OSwicGF0aCI6Ii8yMzQ4MjE5MS8zNjEyNDY0NTctYjc0NDcwNjAtN2NjZC00YThjLWE0MWMtNTVjMTY3OGJmMDg5LnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNDA4MjUlMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjQwODI1VDE2NDMxOVomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTRkZTAxMmU0MjViNjA4NTRmMWRlYzRhYmJkYjNkNWRiNjcxZjRjYWI1MWJkYmMxZmFiZjZmNzFhZTE0ODkwY2MmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0JmFjdG9yX2lkPTAma2V5X2lkPTAmcmVwb19pZD0wIn0.ye5hVTZ-yociOCArw2_KSlvde1MZCQuVYH2LQgul4B0)

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
- `new`: generate a new `segmentation`, a new manually-picked set of `particles`, or a new `surface`, `sphere`, or `filament picking` for segmentation, particle generation or volume resampling.
- `add to exp`: add a layer to the currently selected `experiment` (just a shorthand for `layer.metadata['experiment_id'] = current_exp_id`)
- `slice_thickness`: changes the slicing thickness in all dimensions in napari. Images will be averaged over that thickness, and all particles in the slice will be displayed.

There are also widgets for picking surfaces, spheres and filaments:

- `surface`: process a previously picked `surface picking` layer to generate a surface mesh and distribute particles on it for subtomogram averaging, or resample a tomogram along the surface.
- `sphere`: process a previously picked `sphere picking` layer to generate a sphere mesh and distribute particles on it for subtomogram averaging.
- `filament`: process a previously picked `filament picking` layer to generate a filament and distribute particles on it for subtomogram averaging, or resample a tomogram along the filament.

# References

If you use `blik`, please cite the repo on zenodo and the paper on Plos Biology: [https://doi.org/10.1371/journal.pbio.3002447](https://doi.org/10.1371/journal.pbio.3002447).
