import numpy as np
from xarray import DataArray

from ..abstractblocks import SpatialBlock, SimpleBlock
from ...depictors import PointDepictor


class PointBlock(SpatialBlock, SimpleBlock):
    """
    PointBlock objects for representing points with convenience methods

    PointBlock data should be array-like objects of shape (n, m) representing n points in m dimensions

    order of dimensions along m is:
    2d : (x, y)
    3d : (x. y, z)
    nd : (..., x, y, z)
    """
    _depiction_modes = {'default': PointDepictor}

    def _data_setter(self, data):
        # cast as array
        data = np.asarray(data)

        # coerce single point to right dims
        if data.ndim == 1 and data.size > 0:
            data = data.reshape((1, len(data)))
        if data.size == 0:
            data = data.reshape((0, 3))

        # check ndim of data
        if not data.ndim == 2:
            raise ValueError("data object should have ndim == 2")

        data = DataArray(data, dims=['n', 'spatial'], coords=(range(len(data)), list(self.dims)))
        return data

    @property
    def n(self):
        return len(self.data)

    def _get_named_dimensions(self, dim, remainder=False):
        """
        Get data for a named dimension or multiple named dimensions of the object
        """
        dims = [d for d in dim if d in self.data.spatial]
        if remainder:
            dims.extend(d.item() for d in self.spatial if d.item() not in dims)
        if not dims:
            raise ValueError(f'no such spatial dimension "{dim}"')
        return self.data.sel(spatial=dims)

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
        return f'({self.n}, {self.ndim})'
