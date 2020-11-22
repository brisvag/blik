import numpy as np

from peepingtom.core import MultiBlock, PointBlock, OrientationBlock


class OrientedPointBlock(MultiBlock):
    def __init__(self, positions: np.ndarray, orientations: np.ndarray, **kwargs):
        super().__init__(**kwargs)
        self.positions = PointBlock(positions)
        self.orientations = OrientationBlock(orientations)

    def __shape_repr__(self):
        return f'{self.positions.data.shape}'
