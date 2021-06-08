import numpy as np

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

        return data

    @property
    def n(self):
        return len(self.data)

    def _ndim(self):
        return self.data.shape[-1]

    def __shape_repr__(self):
        return f'({self.n}, {self.ndim})'
