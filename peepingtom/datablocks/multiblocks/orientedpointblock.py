from ..abstractblocks import SpatialBlock, MultiBlock
from ..simpleblocks import PointBlock, OrientationBlock


class OrientedPointBlock(SpatialBlock, MultiBlock):
    def __init__(self, *, positions=(), orientations=(), **kwargs):
        super().__init__(**kwargs)
        self.positions = PointBlock(data=positions, parent=self)
        self.orientations = OrientationBlock(data=orientations, parent=self)

    @property
    def n(self):
        return self.positions.n

    def __shape_repr__(self):
        return f'({self.n}, {self.ndim})'
