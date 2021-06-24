from ..abstractblocks import SpatialBlock, MultiBlock
from ..simpleblocks import PointBlock, PropertyBlock

from ...depictors import MeshDepictor


class MeshBlock(SpatialBlock, MultiBlock):
    """
    Data structure for mesh data
    """
    _block_types = {'vertices': PointBlock, 'faces': PropertyBlock}
    _depiction_modes = {'default': MeshDepictor}

    @property
    def is_3D(self):
        return self.vertices.is_3D()

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

    def __shape_repr__(self):
        return f'{self.vertices.n, self.faces.n}'
