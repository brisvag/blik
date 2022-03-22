# Getting started

## Loading data

From the command line:
```bash
napari /path/to.star /path/to/mrc/files/* [-w blik]
```

Specifying `-w blik` will also open the volume selector widget and set up some things, such as layer visibility and the scale bar.


## Widgets
### Volume Selector

In the `napari` GUI, you'll find the `volume selector`. Select which volume to visualize with the dropdown menu, and the relevant layers will be selected and made visible.


### File Reader
If you need finer control over loading data, you can use the `file reader` widget. You can also start it from the command line with:

```
napari -w blik 'file reader'
```

This widget allows additional arguments compared to the basic `napari` command line interface.

---

`name_regex` is a regex pattern used to extract tomogram names from file names (or things like the `rlnMicrographName` filed in `.star` files). By default, `blik` recognizes files containing `TS_\d+`, and will fall back to `\d+`. For example, the following files will be assigned `TS_001`:

```
CoolSample2_TS_001_something.mrc
Particles_TS_001.star
```

These, instead, will be assigned just `02`:

```
image_02.em
particles_02.tbl
```

---

`names` can be used to whitelist specific tomogram names to load. If passed, anything *not* in the list won't be loaded.

### Filters

Simple imaging filters (such as gaussian) to help with visualization.
