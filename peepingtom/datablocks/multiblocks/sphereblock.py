import numpy as np

from ..abstractblocks import SpatialBlock, MultiBlock
from ..simpleblocks import PointBlock, PropertyBlock


class SphereBlock(SpatialBlock, MultiBlock):
    """
    Represents a spheres defined by center and a radii
    """
    _block_types = {'centers': PointBlock, 'radii': PropertyBlock}

    def set_radii_from_edge_points(self, edge_points):
        self.radii.data = np.linalg.norm(edge_points - self.centers, axis=-1)
