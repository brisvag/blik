import numpy as np

from ..depictor import Depictor


class NapariDepictor(Depictor):
    """
    NapariDepictors are SimpleBlock or MultiBlock wrappers controlling depiction of their contents in napari
    """
    def __init__(self, datablock):
        super().__init__(datablock)
        self.layers = []

    def _make_image_layer(self, image, name, scale=None, **kwargs):
        from napari.layers import Image
        layer = Image(image, name=name, scale=scale, **kwargs)
        self._init_layer(layer)

    def _make_points_layer(self, points, name, **kwargs):
        from napari.layers import Points
        layer = Points(points, name=name, n_dimensional=True, **kwargs)
        self._init_layer(layer)

    def _make_vectors_layer(self, vectors, name, **kwargs):
        from napari.layers import Vectors
        layer = Vectors(vectors, name=name, **kwargs)
        self._init_layer(layer)

    def _make_shapes_layer(self, shape, shape_type, name, **kwargs):
        from napari.layers import Shapes
        layer = Shapes(shape, shape_type=shape_type, name=name, **kwargs)
        self._init_layer(layer)

    def _make_surface_layer(self, vertices, faces, name, values=None, **kwargs):
        from napari.layers import Surface
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

    def purge(self):
        self.layers.clear()
