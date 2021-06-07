from ..abstractblocks import SpatialBlock, MultiBlock
from ..simpleblocks import PointBlock, PropertyBlock

from ...depictors import MeshDepictor


class MeshBlock(SpatialBlock, MultiBlock):
    """
    Data structure for mesh data
    """
    _block_types = {'vertices': PointBlock, 'faces': PropertyBlock}
    _depiction_modes = {'default': MeshDepictor}

    def _ndim(self):
        return self.vertices._ndim()

    @property
    def triangles(self):
        indexes = self.faces.data.to_numpy()
        triangles = self.vertices.data[indexes]
        return triangles

    @property
    def midpoints(self):
        """
        Calculate the midpoints of each triangle in the mesh
        Returns
        -------
        midpoints : (n, m)
                    n midpoints in m dimensions
        """
        return self.triangles.mean(axis=1)
