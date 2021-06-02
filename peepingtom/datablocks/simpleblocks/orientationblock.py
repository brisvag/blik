import numpy as np
import xarray as xr

from ..abstractblocks import SpatialBlock, SimpleBlock


class OrientationBlock(SpatialBlock, SimpleBlock):
    """
    OrientationBlock objects represent orientations in a 2d or 3d space

    Contains factory methods for instantiation from eulerian angles

    data : (n, 2, 2) or (n, 3, 3) array of rotation matrices R
                        R should satisfy Rv = v' where v is a column vector

    """
    def _data_setter(self, data):
        data = np.array(data)
        # check for single matrix case and assert dimensionality
        val_error = ValueError(f'rotation matrices should be of shape '
                               f'(2, 2), (3, 3), (n, 2, 2) or (n, 3, 3), '
                               f'not {data.shape}')
        if data.ndim == 1:
            raise val_error
        if not data.shape[-1] == data.shape[-2]:
            raise val_error
        if not data.shape[-1] in (2, 3):
            raise val_error

        if data.ndim == 2:
            m = data.shape[-1]
            data = data.reshape((1, m, m))

        return xr.DataArray(data, dims=['n', 'spatial', 'spatial2'],
                            coords=(range(len(data)), list(self.dims), list(self.dims)))

    @property
    def n(self):
        return len(self.data)

    def _unit_vector(self, axis: str):
        """
        Get a unit vector along a specified axis which matches the dimensionality of the VectorBlock object
        axis : str, named axis 'x', 'y' (or 'z')
        """
        # check dimensionality
        if self.ndim > 3:
            raise NotImplementedError('Unit vector generation for objects with greater '
                                      'than 3 spatial dimensions is not implemented')

        # initialise unit vector array
        unit_vector = xr.zeros_like(self.data.spatial, dtype=float)

        # construct unit vector
        unit_vector.loc[axis] = 1

        return unit_vector

    def oriented_vectors(self, axis):
        vectors = xr.DataArray(np.dot(self.data, self._unit_vector(axis)),
                               dims=self.data.dims[:-1],
                               coords=[self.data.n, self.data.spatial])
        return vectors

    def zyx_vectors(self):
        axes = [d for d in 'zyx' if d in self.dims]
        all_vectors = {}
        for ax in axes:
            all_vectors[ax] = (self.oriented_vectors(ax).sel(spatial=list(axes)))
        return all_vectors

    @property
    def zyx(self):
        zyx = list('xyz')
        return self.data.sel(spatial=zyx, spatial2=zyx)

    def __shape_repr__(self):
        return f'({self.n}, {self.ndim})'
