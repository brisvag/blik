# Getting started

## Loading data

From the command line:
```bash
blik /path/to.star /path/to/mrc/files/
```

Alternatively, use Blik from within python directly (it's designed with ipython in mind):
```python
import blik 

dataset = blik.read('path_to.mrc')
dataset.show()
```

## Navigating your data
In the napari GUI, you'll find the Blik widget at the bottom left. Select which volume to visualize with the dropdown menu.
Alternatively, you can use `PageUp` and `PageDown` to switch to the previous or next volume.

All napari functionality works as normal, and `dataset` will keep track of which layers come from where. Feel free to add any custom layer: blik won't interfere with them (if it does, please report it in an issue!).

```{note}
Unless you manually generated plots and assigned them to volumes, the `Show / Hide Plots` button will show an empty widget. This is a feature ready for future versions!
```

To get a closer look at all the `DataBlocks` contained in your `DataSet`, try some of the following:
```python
dataset
dataset.volumes
dataset.particles
```
