![logo](docs/images/logo.png)

# PeepingTom

![Codecov branch](https://img.shields.io/codecov/c/github/gutsche-lab/peepingtom/master?label=codecov)
![PyPI](https://img.shields.io/pypi/v/peepingtom)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/peepingtom)

**PeepingTom** is a python tool for visualising and interacting with cryo-ET and subtomogram averaging data. It leverages the fast, multi-dimensional [napari viewer](https://napari.org) and the scientific python stack.

**DISCLAIMER**: this package is in early development phase. Expect frequent bugs and crashes. Please, report them on the issue tracker and ask if anything is unclear!

## Installation

```bash
pip install peepingtom
```

## Basic Usage

From the command line:
```bash
peep /path/to.star /path/to/mrc/files/
```

PeepingTom accepts any combination of files and directory, and will try find the right files and display them in napari. `peep` will also start an ipython shell with the following setup:
```python
import peepingtom as pt
peeper = Peeper([your_data])
viewer = peeper.napari_viewer
```

For more information, check out the help page with `peep -h` and [head over to the docs](https://gutsche-lab.github.io/peepingtom).
