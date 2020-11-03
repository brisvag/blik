from magicgui import magicgui
from magicgui._qt.widgets import QDoubleSlider, QDataComboBox
from napari.layers import Layer, Image, Points
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
    '>': lambda x, y: x >= y,
    '<': lambda x, y: x <= y
}


class MySlider(QDoubleSlider):
    def setMinimum(self, value: float):
        """Set minimum position of slider in float units."""
        super().setMinimum(int(value * self.PRECISION))


def make_property_slider(layer, property_name=None, condition='>'):
    min_value = layer.properties[property_name].min()
    max_value = layer.properties[property_name].max()
    @magicgui(auto_call=True,
              cutoff={'widget_type': MySlider, 'minimum': min_value, 'maximum': max_value, 'fixedWidth': 400})
    def magic_slider(cutoff: float) -> Layer:
        sele = conditions[condition](layer.properties[property_name], cutoff)
        return [(layer.data[sele], {'name': 'result', 'size': 2 }, 'points')]

    return magic_slider.Gui()


class Axis(Enum):
    z = 0
    y = 1
    x = 2


@magicgui(auto_call=True,
          slice_coord={'widget_type': QDoubleSlider, 'fixedWidth': 400, 'maximum': 1},
          mode={'choices': ['average', 'chunk']})
def image_slicer(image: Image, slice_coord: float, slice_size: int, axis: Axis, mode = 'chunk') -> Image:
    im_shape = image.data.shape

    ax_range = im_shape[axis.value] - 1
    ax_range_padded = ax_range - slice_size
    slice_coord_real = int(floor(slice_coord * ax_range_padded + slice_size))
    slice_from = slice_coord_real - floor(slice_size/2)
    slice_to = slice_coord_real + ceil(slice_size/2)

    global zeros
    zeros[:] = 0
    if mode == 'chunk':
        if axis.value == 0:
            zeros[slice_from:slice_to,:,:] = image.data[slice_from:slice_to,:,:]
        elif axis.value == 1:
            zeros[:,slice_from:slice_to,:] = image.data[:,slice_from:slice_to,:]
        elif axis.value == 2:
            zeros[:,:,slice_from:slice_to] = image.data[:,:,slice_from:slice_to]
    elif mode == 'average':
        if axis.value == 0:
            zeros[slice_coord_real,:,:] = image.data[slice_from:slice_to,:,:].mean(axis=0)
        elif axis.value == 1:
            zeros[:,slice_coord_real,:] = image.data[:,slice_from:slice_to,:].mean(axis=1)
        elif axis.value == 2:
            zeros[:,:,slice_coord_real] = image.data[:,:,slice_from:slice_to].mean(axis=2)

    return zeros


def add_widgets(viewer):
    widget = image_slicer.Gui()
    viewer.window.add_dock_widget(widget)
    viewer.layers.events.changed.connect(lambda x: widget.refresh_choices('image'))
    layer_selection_widget = widget.findChild(QDataComboBox, 'image')
    layer_selection_widget.currentTextChanged.connect(update_image)
