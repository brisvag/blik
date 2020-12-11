"""
Depictor interfaces data classes to napari
"""

from napari.layers import Points, Image, Vectors, Shapes

from ...core import MultiBlock


class Depictor:
    """
    Depictors are SimpleBlock or MultiBlock wrappers controlling depiction of their contents
    """
    def __init__(self, datablock, peeper=None):
        self.datablock = datablock

        # hook self to the datablock
        self.datablock.depictor = self
        if isinstance(self.datablock, MultiBlock):
            for block in self.datablock.blocks:
                block.depictor = self

        self.name = self.datablock.name
        self.peeper = peeper

        self.layers = []

    @property
    def viewer(self):
        return self.peeper.viewer

    def make_image_layer(self, image, name, **kwargs):
        return Image(image, name=name, **kwargs)

    def make_points_layer(self, points, name, **kwargs):
        return  Points(points, name=name, **kwargs)

    def make_vectors_layer(self, vectors, name, **kwargs):
        return Vectors(vectors, name=name, **kwargs)

    def make_shapes_layer(self, shape, shape_type, name, **kwargs):
        return Shapes(shape, shape_type=shape_type, name=name, **kwargs)

    def init_layers(self):
        """
        generate the appropriate napari layers and store them
        """
        raise NotImplementedError

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
            self.init_layers()
            self.connect_layers()
        for layer in self.layers:
            self.viewer.add_layer(layer)

    def hide(self, layers=None, delete_layers=False):
        """
        layer_id can be the index or name of a layer or a list of ids
        """
        if layers is None:
            layers = [layer for layer in self.layers]
        if not isinstance(layers, list):
            layers = [layers]
        for layer in layers:
            if layer in self.layers:
                self.viewer.layers.remove(layer)
                if delete_layers:
                    self.layers.remove(layer)

    def update(self):
        """
        update the displayed data based on the current state of the datablock
        """

    def push_changes(self, event):
        """
        push changes in the local layers to the corresponding datablock
        """

    def __repr__(self):
        return f'<{type(self).__name__}[{self.name}]{self.datablock.__shape_repr__()}>'
