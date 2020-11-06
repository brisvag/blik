import pandas as pd


class DataBlock:
    """
    Base class for all classes which can be put into Crates
    """
    def __init__(self, parent=None):
        self.parent = parent


class Particles(DataBlock):
    """
    Positions and orientations of particles in a volume
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


class Image(DataBlock):
    """
    n-dimensional image
    """
    def __init__(self, data, pixel_size=None, **kwargs):
        super().__init__(**kwargs)
        self.data = data
        self.pixel_size = pixel_size

    @property
    def pixel_size(self):
        return self._pixel_size

    @pixel_size.setter
    def pixel_size(self, value):
        self._pixel_size = float(value)


class Model(DataBlock):
    """
    An object representing an underlying geometrical support in an object in an image
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)



