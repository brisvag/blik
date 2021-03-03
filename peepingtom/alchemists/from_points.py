import numpy as np
from scipy.interpolate import Rbf

from ..datablocks import LineBlock, ParticleBlock, PointBlock, OrientationBlock, PropertyBlock
from .alchemist import Alchemist


class PointToLineAlchemist(Alchemist):
    """
    transform a PointBlock into a LineBlock
    """
    def transform(self):
        points = self.inputs[0].data
        self.outputs.append(LineBlock(points))

    def update(self):
        self.outputs[0].data = self.inputs[0].data
        self.outputs[0].update()


class PointToParticleAlchemist(Alchemist):
    """
    transform a PointBlock into a ParticleBlock
    """
    def transform(self):
        points = self.inputs[0].data
        pointblock = PointBlock(points)
        oriblock = OrientationBlock(np.zeros((pointblock.n, pointblock.ndim, pointblock.ndim)))
        propblock = PropertyBlock({})
        self.outputs.append(ParticleBlock(pointblock, oriblock, propblock))

    def update(self):
        self.outputs[0].positions.data = self.inputs[0].data
        self.outputs[0].update()
