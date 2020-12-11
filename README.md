# PeepingTom

![Codecov branch](https://img.shields.io/codecov/c/github/gutsche-lab/peepingtom/master?label=codecov)
![PyPI](https://img.shields.io/pypi/v/peepingtom)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/peepingtom)

**PeepingTom** is a python tool enable easy interaction with cryo-ET and subtomogram averaging data. It leverages the fast, multi-dimensional [napari viewer](https://github.com/napari/napari) and the scientific python stack.

**DISCLAIMER**: this package is in early development phase. Expect frequent bugs and crashes. Feel free to report them on the issue tracker.

## Installation

```bash
pip install peepingtom
```

## Basic Usage

To look at some data:
```python
import peepingtom as pt
p = pt.peep('path_to_data.star')
p = pt.peep('path_to.mrc')
p = pt.peep('path_to_dir', recursive=True, filters='filename_regex')
```

## Tips
To navigate nested attributes in `Peeper`, you can use the convenient dot notation:
```python
p.datablocks.depictor.layers.visible  # visible status of all the napari layers
```
