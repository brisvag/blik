from ..abstractblocks import SpatialBlock, MultiBlock
from ..simpleblocks import PointBlock, OrientationBlock


class OrientedPointBlock(SpatialBlock, MultiBlock):
    _block_types = {'positions': PointBlock, 'orientations': OrientationBlock}

    @property
    def n(self):
        return self.positions.n

    def _ndim(self):
        return self.positions._ndim()

    def __shape_repr__(self):
        return f'({self.n}, {self.ndim})'
