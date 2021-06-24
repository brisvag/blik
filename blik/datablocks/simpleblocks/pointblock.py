import numpy as np

from ..abstractblocks import SpatialBlock, SimpleBlock
from ...depictors import PointDepictor

from ...utils import dim_names_to_indexes


class PointBlock(SpatialBlock, SimpleBlock):
    """
    PointBlock objects for representing points with convenience methods

    PointBlock data should be array-like objects of shape (n, d) representing n points in d dimensions

    Spatial dimensions are ordered xyz
    """
    _depiction_modes = {'default': PointDepictor}

    def _data_setter(self, data):
        # cast as array
        data = np.asarray(data)

        if data.size == 0:
            data = data.reshape(0, 3)

        if data.ndim != 2:
            raise ValueError("point data should have shape (n, d)")

        # coerce to 3 spatial dims
        missing_dims = max(3 - data.shape[1], 0)
        data = np.pad(data, ((0, 0), (0, missing_dims)))

        return data

    @property
    def n(self):
        return len(self.data)

    @property
    def is_3D(self):
        return np.any(self.data[-1])

    def _get_named_dimensions(self, dims):
        """
        Get data for a named dimension or multiple named dimensions of the object
        """
        arrays = []
        for idx in dim_names_to_indexes(dims):
            arrays.append(self.data[:, idx])
        return np.stack(arrays, axis=-1)

    @property
    def x(self):
        return self._get_named_dimensions('x')

    @property
    def y(self):
        return self._get_named_dimensions('y')

    @property
    def z(self):
        return self._get_named_dimensions('z')

    @property
    def xyz(self):
        return self._get_named_dimensions('xyz')

    @property
    def zyx(self):
        return self._get_named_dimensions('zyx')

    @property
    def as_zyx(self):
        """
        returns spatial dimns as zyx but leaves the rest untouched
        """
        rest = self.data[:, :-3]
        return np.concatenate([rest, self.zyx], axis=-1)

    @property
    def center_of_mass(self):
        return np.mean(self.data, axis=0)

    def distance_to(self, point):
        """
        Calculate the euclidean distance between the center of mass of this object and a point

        Parameters
        ----------
        point : array-like object

        Returns : euclidean distance
        -------

        """
        point = np.asarray(point)
        if not point.shape == self.center_of_mass.shape:
            raise ValueError(
                f"shape of point '{point.shape}' does not match shape of center of mass "
                f"'{self.center_of_mass.shape}'")
        return np.linalg.norm(point - self.center_of_mass)

    def __shape_repr__(self):
        return f'{self.data.shape}'
