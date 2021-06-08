# Getting started

## Loading data

From the command line:
```bash
peep /path/to.star /path/to/mrc/files/
```

Alternatively, use PeepingTom from within python directly (it's designed with ipython in mind):
```python
import peepingtom as pt

peeper = pt.peep('path_to.mrc')
peeper.show()
```

## Navigating your data
In the napari GUI, you'll find the PeepingTom widget at the bottom left. Select which volume to visualize with the dropdown menu.
Alternatively, you can use `PageUp` and `PageDown` to switch to the previous or next volume.

All napari functionality works as normal, and `peeper` will keep track of which layers come from where. Feel free to add any custom layer: peepingtom won't interfere with them (if it does, please report it in an issue!).

```{note}
Unless you manually generated plots and assigned them to volumes, the `Show / Hide Plots` button will show an empty widget. This is a feature ready for future versions!
```

To get a closer look at all the `DataBlocks` contained in your `Peeper`, try some of the following:
```python
peeper
peeper.volumes
peeper.particles
```
