"""
Gui elements for interfacing peeper and napari
"""

from enum import Enum
from math import floor, ceil
from inspect import signature

import numpy as np
import napari
from magicgui import magicgui
from magicgui._qt.widgets import QDoubleSlider, QDataComboBox
from napari.layers import Layer, Image, Points


class MySlider(QDoubleSlider):
    def setMinimum(self, value: float):
        """Set minimum position of slider in float units."""
        super().setMinimum(int(value * self.PRECISION))


def make_property_widgets(points_layer, property_conditions: dict, output_layer='result'):
    """
    conditions can be strings such as:
        - >, <, >=, <=: continuous properties, make sliders to set the cutoff
        - 'check': property is categorical, make a checkbox for each unique value
    """
    continuous_props = []
    categorical_props = {}
    for p, c in property_conditions.items():
        if c == 'check':
            categorical_props.append(p)
        else:
            continuous_props[p] = {}
            continuous_props[p]['cond'] = c

    for prop, params in continuous_props:
        params['min'] = points_layer.properties[prop].min()
        params['max'] = points_layer.properties[prop].max()

    magic_kwargs = {}
    for prop, params in continuous_props:
        magic_kwargs[prop] = {'widget_type': MySlider, 'minimum': params['min'], 'maximum': params['max']}
    for prop in categorical_props:
        pass
    # programmatically generate function call
    func_lines = []
    func_lines.append(f'def magic_slider(layer: Points, {": float, ".join(property_names)}: float) -> Layer:')
    func_lines.append(f'sele = np.ones(len(layer.data))')
    for prop, cond in zip(property_names, conditions):
        func_lines.append(f'sele_{prop} = layer.properties["{prop}"] {cond} {prop}')
        func_lines.append(f'sele = np.logical_and(sele, sele_{prop})')
    func_lines.append(f'return [(layer.data[sele], {{"name": "{output_layer}", "size": 3 }}, "points")]')
    func = '\n    '.join(func_lines)
    # make the widget
    exec(func, globals())
    slider_gui = magicgui(magic_slider, auto_call=True, **magic_kwargs)

    return slider_gui.Gui()


@magicgui(auto_call=True)
def checkboxes(class_0: True, class_1: True, class_2: True):
    pass


class Axis(Enum):
    z = 0
    y = 1
    x = 2

zeros = []

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
    layer_selection_widget.currentTextChanged.connect()
