import numpy as np

from ..datablocks import LineBlock, ParticleBlock, PointBlock, OrientationBlock, PropertyBlock
from .alchemist import Alchemist


class PointToLineAlchemist(Alchemist):
    """
    transform a PointBlock into a LineBlock
    """
    def transform(self):
        points = self.inputs[0].data
        self.outputs.append(LineBlock(data=points))

    def update(self):
        self.outputs[0].data = self.inputs[0].data
        self.outputs[0].update()


class PointToParticleAlchemist(Alchemist):
    """
    transform a PointBlock into a ParticleBlock
    """
    def transform(self):
        points = self.inputs[0].data
        pointblock = PointBlock(data=points)
        oriblock = OrientationBlock(data=np.zeros((pointblock.n, pointblock.ndim, pointblock.ndim)))
        propblock = PropertyBlock(data={})
        self.outputs.append(ParticleBlock(positions_data=pointblock,
                                          orientations_data=oriblock,
                                          properties_data=propblock))

    def update(self):
        self.outputs[0].positions.data = self.inputs[0].data
        self.outputs[0].update()
