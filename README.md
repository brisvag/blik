# PeepingTom

![Codecov branch](https://img.shields.io/codecov/c/github/gutsche-lab/peepingtom/master?label=codecov)
![PyPI](https://img.shields.io/pypi/v/peepingtom)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/peepingtom)

**PeepingTom** is a python tool for visualising and interacting with cryo-ET and subtomogram averaging data. It leverages the fast, multi-dimensional [napari viewer](https://github.com/napari/napari) and the scientific python stack.

**DISCLAIMER**: this package is in early development phase. Expect frequent bugs and crashes. Please, report them on the issue tracker and ask if anything is unclear!

## Installation

```bash
pip install peepingtom
```

## Usage

From the command line, try:
```bash
peep /path/to.star /path/to/mrc/files/
```
PeepingTom accepts any combination of files and directory, and will try find the right files and display them in napari. `peep` will also start an ipython shell with the following setup:
```python
import peepingtom as pt
peeper = Peeper([your_data])
viewer = peeper.napari_viewer
```

For more customizability check out:
```bash
peep -h
```

Alternatively, use PeepingTom from within python directly (it's designed with ipython in mind):
```python
import peepingtom as pt

peeper = pt.peep('path_to.mrc')
peeper.show()
```

To get a closer view at all the `DataBlocks` contained in your `Peeper`:
```python
peeper.pprint()
peeper.volumes
```

## Tips
To navigate nested attributes in `Peeper`, you can use the convenient `DispatchList`. Some methods of `Peeper` return this type of list, which is printed as `*[elements]*`. Try:
```python
peeper.datablocks.name
# *[name1, name2, name3, ...]*
```

It works for method calls and setting values...
```python
peeper.napari_layers.visible = False
```

and you even can dispatch getitem calls with `.disp`, similarly to pandas `.loc`:
```python
peeper.datablocks.disp[:3]  # returns a view of the first 3 elements (if possible) of each datablock
```
