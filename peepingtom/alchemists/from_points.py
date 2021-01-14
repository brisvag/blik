import numpy as np
from scipy.interpolate import Rbf

from ..datablocks import LineBlock, ParticleBlock, PointBlock, OrientationBlock, PropertyBlock
from .alchemist import Alchemist


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


class PointToMeshAlchemist(Alchemist):
    def __init__(self, pointblock):
        super().__init__({'points': pointblock})

    def transform(self):
        x, y, z = self.inputs['points'].data.T
        x_grid = np.linspace(0, x.max(), 50)
        y_grid = np.linspace(0, y.may(), 50)
        B1, B2 = np.meshgrid(x_grid, y_grid, indexing='xy')
        Z = np.zeros((x.size, z.size))

        spline = Rbf(x,y,z,function='thin_plate',smooth=5, episilon=5)

        Z = spline(B1,B2)
        fig = plt.figure(figsize=(10,6))
        ax = axes3d.Axes3D(fig)
        ax.plot_wireframe(B1, B2, Z)
        ax.plot_surface(B1, B2, Z,alpha=0.2)
        ax.scatter3D(x,y,z, c='r')
