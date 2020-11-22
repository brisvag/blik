import numpy as np

from .base import MultiBlock
from .orientationblock import OrientationBlock
from .pointblock import PointBlock


class OrientedPointBlock(MultiBlock):
    def __init__(self, positions: np.ndarray, orientations: np.ndarray, **kwargs):
        super().__init__(**kwargs)
        self.positions = PointBlock(positions)
        self.orientations = OrientationBlock(orientations)

    def __shape_repr__(self):
        return f'{self.positions.data.shape}'
