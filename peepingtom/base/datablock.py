from abc import ABC, abstractmethod

import pandas as pd
from ..utils.components import Child


class DataBlock(Child, ABC):
    """
    Base class for all classes which can be put into Crates for subsequent visualisation

    Examples include geometric primitives such as Points, Line, Sphere

    DataBlock objects must implement a data setter method as _data_setter which sets the value of DataBlock._data

    Calling __getitem__ on a DataBlock will call __getitem__ on its data property
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        return self._data_setter(value)

    @abstractmethod
    def _data_setter(self, *args):
        """
        abstract method which sets the data property of the object
        """
        self._data = [arg for arg in args]

    def __getitem__(self, item):
        return self.data[item]




class Points(DataBlock):
    def __init__(self, points, **kwargs):
        super().__init__(**kwargs)

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






