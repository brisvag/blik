from magicgui import magicgui
from magicgui._qt.widgets import QDoubleSlider
from napari.layers import Layer, Image
import napari
import numpy as np
from enum import Enum
from math import floor, ceil

colors = {
    'transparent': [0, 0, 0, 0],
    'white': [1, 1, 1, 1],
    'black': [0, 0, 0, 1]
}

conditions = {
    '>': lambda x, y: x > y,
    '<': lambda x, y: x < y
}


def make_property_slider(layer_type, property_name=None, condition='>', max_value=None, min_value=0):
    @magicgui(auto_call=True,
              cutoff={'widget_type': QDoubleSlider, 'minimum': min_value, 'maximum': max_value, 'fixedWidth': 400})
    def magic_slider(layer: layer_type, cutoff: float):
        sele = conditions[condition](layer.properties[property_name], cutoff)
        layer.face_color[sele] = colors['transparent']
        layer.edge_color[sele] = colors['transparent']
        layer.face_color[~sele] = colors['white']
        layer.edge_color[~sele] = colors['black']
        layer.refresh_colors()

    return magic_slider.Gui()


class Axis(Enum):
    z = 0
    y = 1
    x = 2


@magicgui(auto_call=True,
          slice_coord={'widget_type': QDoubleSlider, 'fixedWidth': 400, 'maximum': 1},
          mode={'choices': ['average', 'chunk']})
def image_slicer(image: Image, slice_coord: float, slice_size: int, axis: Axis, mode = 'chunk') -> Image:
    ax_range = image.data.shape[axis.value] - 1
    ax_range_padded = ax_range - slice_size
    slice_coord_real = int(floor(slice_coord * ax_range_padded + slice_size))
    slice_from = slice_coord_real - floor(slice_size/2)
    slice_to = slice_coord_real + ceil(slice_size/2)

    new_image = np.zeros_like(image.data)
    if mode == 'chunk':
        if axis.value == 0:
            new_image[slice_from:slice_to,:,:] = image.data[slice_from:slice_to,:,:]
        elif axis.value == 1:
            new_image[:,slice_from:slice_to,:] = image.data[:,slice_from:slice_to,:]
        elif axis.value == 2:
            new_image[:,:,slice_from:slice_to] = image.data[:,:,slice_from:slice_to]
    elif mode == 'average':
        if axis.value == 0:
            new_image[slice_coord_real,:,:] = image.data[slice_from:slice_to,:,:].mean(axis=0)
        elif axis.value == 1:
            new_image[:,slice_coord_real,:] = image.data[:,slice_from:slice_to,:].mean(axis=1)
        elif axis.value == 2:
            new_image[:,:,slice_coord_real] = image.data[:,:,slice_from:slice_to].mean(axis=2)

    return new_image
