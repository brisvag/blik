import pandas as pd


class BaseData:
    pass


class Particles(BaseData):
    """
    represent positions and orientations of particles in a volume
    coordinates: (n, m+3), with m=additional dimensions. Last 3 are in order zyx
    orientation_matrices: (n, 3, 3), transformation from Z to particle (order zyx)
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


class Image(BaseData):
    """
    n-dimensional image of shape (#m, z, y, x), with m additional dimensions
    """
    def __init__(self, data):
        self.data = data


class DataBlock(BaseData, list):
    """
    represents a collection of data objects within the same volumetric reference space
    """
    # TODO: add napari-like indexing by attribute or by type
    def __init__(self, iterable=()):
        if not all([isinstance(i, BaseData) for i in iterable]):
            raise Exception('DataBlock can only collect BaseData objects')
