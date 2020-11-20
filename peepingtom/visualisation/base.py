"""
Depictor interfaces data classes to napari
"""

from napari.components.layerlist import LayerList
from napari.layers import Points

from ..core import MultiBlock


class Depictor:
    """
    Depictors are DataBlock or MultiBlock wrappers controlling depiction of their contents
    """
    def __init__(self, datablock, peeper=None, name='NoName'):
        self.datablock = datablock

        # hook self to the datablock
        self.datablock.depictor = self
        if isinstance(self.datablock, MultiBlock):
            for block in self.datablock.blocks:
                block.depictor = self

        self.name = name
        self.peeper = peeper

        self.layers = LayerList()

    @property
    def viewer(self):
        return self.peeper.viewer

    def make_layers(self):
        """
        generate the appropriate napari layers and store them
        """

    def connect_layers(self):
        """
        connects events on layer data to an update of the relative datablock
        """
        for layer in self.layers:
            layer.events.data.connect(self.push_changes)

    def draw(self, viewer=None, remake_layers=False):
        """
        creates a new napari viewer if not present
        displays the contents of the datablock
        """
        # create a new viewer if necessary
        if viewer is None:
            viewer = self.viewer
        if remake_layers or not self.layers:
            self.make_layers()
            self.connect_layers()
        for layer in self.layers:
            self.viewer.add_layer(layer)

    def hide(self, layers=None, delete_layers=False):
        """
        layer_id can be the index or name of a layer or a list of ids
        """
        if layers is None:
            layers = [l for l in self.layers]
        if not isinstance(layers, list):
            layers = [layers]
        for l in layers:
            if l in self.layers:
                self.viewer.layers.remove(l)
                if delete_layers:
                    self.layers.remove(l)

    def update(self):
        """
        update the displayed data based on the current state of the datablock
        """

    def push_changes(self, event):
        """
        push changes in the local layers to the corresponding datablock
        """

    def __repr__(self):
        return f'<{type(self).__name__}:{self.datablock}>'
