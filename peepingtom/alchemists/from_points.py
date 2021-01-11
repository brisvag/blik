import numpy as np

from ..datablocks import LineBlock, ParticleBlock, PointBlock, OrientationBlock, PropertyBlock
from .base import Alchemist


class PointToLineAlchemist(Alchemist):
    """
    transform a PointBlock into a LineBlock
    """
    def __init__(self, pointblock):
        super().__init__({'points': pointblock})

    def transform(self):
        points = self.inputs['points'].data
        if 'line' not in self.outputs:
            self.outputs['line'] = LineBlock(points)
        else:
            self.outputs['line'].data = points


class PointToParticleAlchemist(Alchemist):
    """
    transform a PointBlock into a ParticleBlock
    """
    def __init__(self, pointblock):
        super().__init__({'points': pointblock})

    def transform(self):
        points = self.inputs['points'].data
        if 'particles' not in self.outputs:
            pointblock = PointBlock(points)
            oriblock = OrientationBlock(np.zeros((pointblock.n, pointblock.ndim, pointblock.ndim)))
            propblock = PropertyBlock({})
            self.outputs['particles'] = ParticleBlock(pointblock, oriblock, propblock)
        else:
            self.outputs['particles'].positions.data = points
