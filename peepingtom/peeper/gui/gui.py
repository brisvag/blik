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
    available_conds = ('>', '<', '==', '<=', '>=')
    #sanity check:
    categorical_props = {}
    continuous_props = {}
    for p, c in property_conditions.items():
        if p not in points_layer.properties:
            raise ValueError(f'{p} is not a property of {points_layer}')
        if c == 'check':
            categorical_props[p] = {}
            categorical_props[p]['values'] = np.unique(points_layer.properties[p])
        elif c in available_conds:
            continuous_props[p] = {}
            continuous_props[p]['cond'] = c
            continuous_props[p]['min'] = points_layer.properties[p].min()
            continuous_props[p]['max'] = points_layer.properties[p].max()
        else:
            raise ValueError("conditions can only be 'check' or one of {available_conds}")

    magic_kwargs = {}
    for prop, params in continuous_props.items():
        magic_kwargs[prop] = {'widget_type': MySlider, 'minimum': params['min'], 'maximum': params['max']}
    # programmatically generate function call
    func_lines = []
    func_lines.append(f'def magic_widget(layer: Points, {": float, ".join(continuous_props)}: float) -> Layer:')
    func_lines.append(f'sele = np.ones(len(layer.data))')
    for prop, params in continuous_props.items():
        func_lines.append(f'sele_{prop} = layer.properties["{prop}"] {params["cond"]} {prop}')
        func_lines.append(f'sele = np.logical_and(sele, sele_{prop})')
    func_lines.append(f'return [(layer.data[sele], {{"name": "{output_layer}", "size": 3 }}, "points")]')
    func = '\n    '.join(func_lines)
    # make the widget
    exec(func, globals())
    widget_gui = magicgui(magic_widget, auto_call=True, **magic_kwargs)

    return widget_gui.Gui()


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
