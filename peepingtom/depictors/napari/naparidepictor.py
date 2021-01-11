from napari.layers import Points, Image, Vectors, Shapes


class NapariDepictor:
    """
    NapariDepictors are SimpleBlock or MultiBlock wrappers controlling depiction of their contents in napari
    """
    def __init__(self, datablock):
        self.datablock = datablock
        self.layers = []
        self.depict()

    @property
    def name(self):
        return self.datablock.name

    def make_image_layer(self, image, name, **kwargs):
        layer = Image(image, name=name, **kwargs)
        self._init_layer(layer)

    def make_points_layer(self, points, name, **kwargs):
        layer = Points(points, name=name, **kwargs)
        self._init_layer(layer)

    def make_vectors_layer(self, vectors, name, **kwargs):
        layer = Vectors(vectors, name=name, **kwargs)
        self._init_layer(layer)

    def make_shapes_layer(self, shape, shape_type, name, **kwargs):
        layer = Shapes(shape, shape_type=shape_type, name=name, **kwargs)
        self._init_layer(layer)

    def _init_layer(self, layer):
        """
        connects events on layer data to an update of the relative datablock
        and adds it to the depictor's layer list
        """
        layer.events.data.connect(self.changed)
        self.layers.append(layer)

    def depict(self):
        """
        create layers according to the depiction parameters
        """
        raise NotImplementedError

    def show(self, viewer):
        """
        displays the depicted layers in a napari viewer
        """
        for layer in self.layers:
            if layer not in viewer.layers:
                viewer.layers.append(layer)

    def hide(self, viewer):
        """
        hides the depiction from a viewer
        """
        for layer in self.layers:
            if layer in viewer.layers:
                viewer.layers.remove(layer)

    def update(self):
        """
        update the displayed data based on the current state of the datablock
        """

    def changed(self, event):
        """
        fired when layer data in napari is changed. Subclasses can overload this method with
        the logic to update the data in the datablock accordingly
        """

    def __repr__(self):
        return f'{type(self).__name__}{self.datablock.__name_repr__()}'
