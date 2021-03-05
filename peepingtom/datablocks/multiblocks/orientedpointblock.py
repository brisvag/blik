from .multiblock import MultiBlock
from ..simpleblocks import PointBlock, OrientationBlock


class OrientedPointBlock(MultiBlock):
    def __init__(self, positions=(), orientations=(), pixel_size=None, **kwargs):
        super().__init__(**kwargs)
        self.positions = PointBlock(positions, pixel_size=pixel_size)
        self.orientations = OrientationBlock(orientations)

    @property
    def n(self):
        return self.positions.n

    @property
    def ndim(self):
        return self.positions.ndim

    @property
    def dims(self):
        return self.positions.dims

    @property
    def pixel_size(self):
        return self.positions.pixel_size
