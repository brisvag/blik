import pandas as pd


class BlockBaseData:
    """
    base class for all dataclasses which can be put combined into DataBlocks
    """
    def __init__(self):
        self.parent = None


class Particles(BlockBaseData):
    """
    represent positions and orientations of particles in a volume
    coordinates: (n, m+3), with m=additional dimensions. Last 3 are in order xyz
    orientation_matrices: (n, 3, 3) ndarray R which rotates xyz column vectors v when matrix multiplied Rv
    properties: dataframe of length n with additional particle properties
    """
    def __init__(self, coordinates, orientation_matrices, properties=None):
        super().__init__()
        self.coords = coordinates
        if properties is None:
            properties = pd.DataFrame()
        self.properties = properties
        self.orientations = orientation_matrices

    def prop_as_dict(self):
        """
        properties as dictionaries of numpy arrays
        """
        return dict(zip(self.properties.keys(), self.properties.values))

    def ori_as_vectors(self, from_vector='z'):
        unit_vectors = {'x': [1, 0, 0],
                        'y': [0, 1, 0],
                        'z': [0, 0, 1]}
        if isinstance(from_vector, str):
            vect = unit_vectors.get(from_vector)
        else:
            vect = from_vector

        if vect is None:
            vect = unit_vectors.get('z')

        return self.orientations @ vect


class Image(BlockBaseData):
    """
    n-dimensional image
    """
    def __init__(self, data, pixel_size=None):
        super().__init__()
        self.data = data
        self.pixel_size = pixel_size

    @property
    def pixel_size(self):
        return self._pixel_size

    @pixel_size.setter
    def pixel_size(self, value):
        return float(value)


class Image2D(Image):
    """
    2 dimensional image of shape (y, x)
    """
    def __init__(self, data, **kwargs):
        super().__init__(data, **kwargs)

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        assert len(data.shape) == 2
        self._data = data


class Image3D(Image):
    """
    3 dimensional image of shape (z, y, x)
    """
    def __init__(self, data, **kwargs):
        super().__init__(data, **kwargs)

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        assert len(data.shape) == 2
        self._data = data


