from ..abstractblocks import SpatialBlock, MultiBlock
from ..simpleblocks import PointBlock, OrientationBlock


class OrientedPointBlock(SpatialBlock, MultiBlock):
    _block_types = {'positions': PointBlock, 'orientations': OrientationBlock}

    @property
    def n(self):
        return self.positions.n

    @property
    def is_3D(self):
        return self.positions.is_3D

    def __shape_repr__(self):
        return f'({self.n})'
