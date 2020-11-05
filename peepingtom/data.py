import pandas as pd

class Data:
    pass


class Particles(Data):
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

    def ori_as_vectors(self):
        """
        """
        # accept any arbitrary vector(s), with special cases for unit vectors xyz


class Image(Data):
    """
    n-dimensional image of shape (#m, z, y, x), with m additional dimensions
    """
    def __init__(self, data):
        self.data = data
