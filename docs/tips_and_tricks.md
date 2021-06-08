# Tips and Tricks

## File names and volumes
To load your data into a `Peeper`, peepingtom needs to know how to divide it in "volumes". By default, peepingtom will try to split everything based on file names (or things like the `rlnMicrographName` filed in `.star` files) and using some [regex pattern](https://en.wikipedia.org/wiki/Regular_expression) to decide which data belongs to the same 3D volumes.

By default, peepingtom recognizes files containing `TS_\d+`, and will fall back to `\d+`. For example, the following will be part of the `TS_001` volume:
```
CoolSample2_TS_001_something.mrc
Particles_TS_001.star
```

These, instead, will be put simply in `02`:
```
image_02.em
particles_02.tbl
```

Anything else ends up in its own `None_X` volume. If your data follows a different naming scheme, you can provide a [custom regex pattern](https://regex101.com/):
```python
pt.peep(YOUR_DATA, name_regex='\d_\w+')
```

## DispatchList
To navigate nested attributes in `Peeper`, you can use the convenient `DispatchList`. Some methods of `Peeper` return this type of list, which is printed as `*[elements]*`. Try:
```python
peeper.datablocks.name
# *[name1, name2, name3, ...]*
```

It works for method calls and setting values...
```python
peeper.particles.pixel_size = 10
peeper.particles.
```

... and you can even dispatch getitem calls with `.disp`, similarly to pandas' `.loc`:
```python
peeper.datablocks.disp[:3]  # returns a view of the first 3 elements (if possible) of each datablock
```
