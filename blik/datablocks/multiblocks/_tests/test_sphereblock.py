import numpy as np

from blik.datablocks.multiblocks.sphereblock import SphereBlock


def test_sphereblock():
    block = SphereBlock(centers_data=np.zeros((2, 3)), radii_data=np.zeros(2))
    assert isinstance(block, SphereBlock)
    block.set_radii_from_edge_points(np.array([[1, 0, 0]]))
    assert np.all(block.radii.data == 1)
