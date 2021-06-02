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
    def triangles(self):
        # TODO: can't figure out how to do it with xarray
        indexes = self.faces.data.to_numpy()
        triangles = self.vertices.data.values[indexes]
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
