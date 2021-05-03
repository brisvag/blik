import numpy as np
from xarray import DataArray

from .simpleblock import SimpleBlock
from ...depictors import PointDepictor


class PointBlock(SimpleBlock):
    """
    PointBlock objects for representing points with convenience methods

    PointBlock data should be array-like objects of shape (n, m) representing n points in m dimensions

    order of dimensions along m is:
    2d : (x, y)
    3d : (x. y, z)
    nd : (..., x, y, z)
    """
    _depiction_modes = {'default': PointDepictor}

    def __init__(self, data=(), pixel_size=None, **kwargs):
        self.pixel_size = pixel_size  # no checking here, or we screw up lazy loading
        super().__init__(data, **kwargs)
        # TODO this is a workaround until napari #2347 is fixed

    def _data_setter(self, data):
        if isinstance(data, DataArray):
            return data
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

        dims = ['x', 'y', 'z']
        data = DataArray(data, dims=['n', 'spatial'], coords=(range(len(data)), dims[:data.shape[1]]))

        # set pixel_size if needed
        if self.pixel_size is None:
            pixel_size = np.ones(len(data.spatial))
            pixel_size = np.broadcast_to(pixel_size, len(data.spatial))
            self.pixel_size = np.array(pixel_size)

        return data

    @property
    def ndim(self):
        """
        as ndim for numpy arrays, but treating the points as a sparse matrix.
        returns the number of dimensions (spatial or not) describing the points
        """
        return self.data.shape[1]

    @property
    def dims(self):
        return tuple(self.data.spatial.data)

    def _get_named_dimensions(self, dim):
        """
        Get data for a named dimension or multiple named dimensions of the object
        """
        dim = list(dim)
        return self.data.sel(spatial=dim)

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

    def as_zyx(self):
        """
        return the data with the order of the spatial axes switched to 'zyx' style rather than 'xyz'

        Returns
        -------
        correct view into data no matter the dimensionality
        """
        spatial = sorted([d for d in self.data.spatial.values if d in 'xyz'], reverse=True)
        rest = [d for d in self.data.spatial.values if d not in spatial]
        new_order = list(rest + spatial)
        return self.data.sel(spatial=new_order)

    @property
    def n(self):
        return len(self)

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

    def to_line(self):
        from ...alchemists import PointToLineAlchemist
        self.alchemists.append(PointToLineAlchemist(self))
