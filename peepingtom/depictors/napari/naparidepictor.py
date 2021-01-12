from napari.layers import Points, Image, Vectors, Shapes

from ..depictor import Depictor


class NapariDepictor(Depictor):
    """
    NapariDepictors are SimpleNapari or MultiNapari wrappers controlling depiction of their contents in napari
    """
    def __init__(self, datablock):
        self.layers = []
        super().__init__(datablock)

    def _make_image_layer(self, image, name, **kwargs):
        layer = Image(image, name=name, **kwargs)
        self._init_layer(layer)

    def _make_points_layer(self, points, name, **kwargs):
        layer = Points(points, name=name, **kwargs)
        self._init_layer(layer)

    def _make_vectors_layer(self, vectors, name, **kwargs):
        layer = Vectors(vectors, name=name, **kwargs)
        self._init_layer(layer)

    def _make_shapes_layer(self, shape, shape_type, name, **kwargs):
        layer = Shapes(shape, shape_type=shape_type, name=name, **kwargs)
        self._init_layer(layer)

    def _init_layer(self, layer):
        """
        connects events on layer data to an update of the relative datablock
        and adds it to the depictor's layer list
        """
        layer.events.data.connect(self.changed)
        self.layers.append(layer)

    def show(self, viewer):
        for layer in self.layers:
            if layer not in viewer.layers:
                viewer.layers.append(layer)

    def hide(self, viewer):
        for layer in self.layers:
            if layer in viewer.layers:
                viewer.layers.remove(layer)
