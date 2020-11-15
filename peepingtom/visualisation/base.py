"""
Depictor interfaces data classes to napari
"""

from types import MethodType

from napari.components.layerlist import LayerList

from ..core import GroupBlock


class Depictor:
    """
    Depictors are DataBlock or GroupBlock wrappers able controlling depiction of their contents in napari
    """

    def __init__(self, datablock, peeper, name='NoName'):
        self.datablock = datablock

        # this hack updates DataBlock.updated() with a new version that calls Depictor.update()
        def updated_patch(slf):
            slf.depictor.update()

        if isinstance(self.datablock, GroupBlock):
            for child in self.datablock.children:
                child.updated = MethodType(updated_patch, child)
                child.depictor = self
        self.datablock.updated = MethodType(updated_patch, self.datablock)

        # hook self to the datablock
        self.datablock.depictor = self

        self.name = name
        self.peeper = peeper
        self.layers = LayerList()

    @property
    def viewer(self):
        return self.peeper.viewer

    def draw(self, viewer=None, remake_layers=False):
        """
        creates a new napari viewer if not present
        displays the contents of the datablock
        """
        # create a new viewer if necessary
        if viewer is None:
            viewer = self.viewer
        if self.layers and not remake_layers:
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
        pass
