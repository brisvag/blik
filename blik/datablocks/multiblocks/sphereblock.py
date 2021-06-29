import numpy as np

from ..abstractblocks import SpatialBlock, MultiBlock
from ..simpleblocks import PointBlock, PropertyBlock


class SphereBlock(SpatialBlock, MultiBlock):
    """
    Represents a set of spheres defined by centers and a radii
    """
    _block_types = {'centers': PointBlock, 'radii': PropertyBlock}

    @property
    def is_3D(self):
        return True

    def set_radii_from_edge_points(self, edge_points):
        self.radii.data = np.linalg.norm(edge_points - self.centers, axis=-1)
