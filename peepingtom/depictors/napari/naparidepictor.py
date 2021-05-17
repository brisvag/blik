import numpy as np
from napari.layers import Points, Image, Vectors, Shapes, Surface

from ..depictor import Depictor


class NapariDepictor(Depictor):
    """
    NapariDepictors are SimpleBlock or MultiBlock wrappers controlling depiction of their contents in napari
    """
    def __init__(self, datablock):
        self.layers = []
        super().__init__(datablock)

    def _make_image_layer(self, image, name, scale=None, **kwargs):
        layer = Image(image, name=name, scale=scale, **kwargs)
        self._init_layer(layer)

    def _make_points_layer(self, points, name, scale=None, **kwargs):
        layer = Points(points, name=name, scale=scale, n_dimensional=True, **kwargs)
        self._init_layer(layer)

    def _make_vectors_layer(self, vectors, name, scale=None, **kwargs):
        layer = Vectors(vectors, name=name, **kwargs)
        # TODO this is a workaround until napari #2347 is fixed
        if scale is not None:
            layer.scale = scale
        self._init_layer(layer)

    def _make_shapes_layer(self, shape, shape_type, name, **kwargs):
        layer = Shapes(shape, shape_type=shape_type, name=name, **kwargs)
        self._init_layer(layer)

    def _make_surface_layer(self, vertices, faces, name, values=None, **kwargs):
        if values is None:
            values = np.ones(vertices.shape[0])
        data = (vertices, faces, values)
        layer = Surface(data, name=name, **kwargs)
        self._init_layer(layer)

    def _init_layer(self, layer):
        """
        connects events on layer data to an update of the relative datablock
        and adds it to the depictor's layer list
        """
        layer.events.data.connect(self.changed)
        self.layers.append(layer)
