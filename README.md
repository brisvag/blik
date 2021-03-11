# PeepingTom

![Codecov branch](https://img.shields.io/codecov/c/github/gutsche-lab/peepingtom/master?label=codecov)
![PyPI](https://img.shields.io/pypi/v/peepingtom)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/peepingtom)

**PeepingTom** is a python tool for visualising and interacting with cryo-ET and subtomogram averaging data. It leverages the fast, multi-dimensional [napari viewer](https://github.com/napari/napari) and the scientific python stack.

**DISCLAIMER**: this package is in early development phase. Expect frequent bugs and crashes. Feel free to report them on the issue tracker.

## Installation

```bash
pip install peepingtom
```

## Usage

From the command line, try:
```bash
peep /path/to.star /path/to/mrc/files
```
PeepingTom accepts any combination of files and directory, and will try find the right files and display them in napari. `peep` will also start an ipython shell with the following setup:
```python
import peepingtom as pt
p = Peeper([your_data])
```

For more customizability (such as filtering) check out:
```bash
peep -h
```

Alternatively, use PeepingTom from within python directly (it's designed with ipython in mind):
```python
import peepingtom as pt

p = pt.peep('path_to.mrc')
p.show()
```

To get a closer view at all the `DataBlocks` contained in your `Peeper`:
```python
p.pprint()
p.volumes()
```

## Tips
To navigate nested attributes in `Peeper`, you can use the convenient `DispatchList`. Some methods of `Peeper` return this type of list, which is printed as `*[elements]`. Try:
```python
p.datablocks.name
# *[name1, name2, name3, ...]
```

It works for method calls and setting values as well!
```python
p.napari_layers.visible = False
```
