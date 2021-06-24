import numpy as np

from ..abstractblocks import SpatialBlock, SimpleBlock


class OrientationBlock(SpatialBlock, SimpleBlock):
    """
    OrientationBlock objects represent orientations in nd space

    data must be (n, 3, 3) or (n, 2, 2), and will be reshaped to (n, 3, 3)

    order of spatial dimensions is xyz
    """
    def _data_setter(self, data):
        data = np.array(data)
        # check for single matrix case and assert dimensionality
        if data.ndim < 3:
            data = data[np.newaxis]
        if data.shape[-1] != data.shape[-2] or data.shape[-1] not in (2, 3):
            raise ValueError(f'rotation matrices should be of shape '
                             f'(n, 2, 2) or (n, 3, 3), '
                             f'not {data.shape}')

        # coerce to 3D
        if data.shape[-1] == 2:
            data = np.pad(data, ((0, 0), (0, 1), (0, 1)))
            data[:, -1, -1] = 1
        return data

    @property
    def n(self):
        return len(self.data)

    @property
    def is_3D(self):
        return np.any(self.data[:, 2, :2]) \
            and np.any(self.data[:, :2, 2]) \
            and np.any(self.data[:, 2, 2] != 1)

    @property
    def as_zyx(self, ):
        return self.data[:, ::-1, ::-1]

    def __shape_repr__(self):
        return f'({self.n})'
