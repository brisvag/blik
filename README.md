# PeepingTom

![Codecov branch](https://img.shields.io/codecov/c/github/gutsche-lab/peepingtom/master?label=codecov)
![PyPI](https://img.shields.io/pypi/v/peepingtom)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/peepingtom)

Peeping at Tomography data.

**DISCLAIMER**: this package is in early development phase. Expect frequent bugs and crashes. Feel free to report them on the issue tracker.

**PeepingTom** is a python tool to simplify and enable interaction with cryo-ET and subtomogram averaging data. It leverages the fast, multi-dimensional [napari viewer](https://github.com/napari/napari) and the scientific python stack.

## Installation

```
pip install peepingtom
```

## Basic Usage

While the higher level API is still in early development, some tools are already functional.

```
from peepingtom import ParticlePeeper
p = ParticlePeeper(path_to_data.star)
```
