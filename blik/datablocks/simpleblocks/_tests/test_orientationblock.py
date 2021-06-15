import numpy as np
from numpy.testing import assert_array_equal
from eulerangles import euler2matrix

from blik.datablocks.simpleblocks.orientationblock import OrientationBlock

# test data for orientationblock
# orientations
rot = np.zeros(50)
tilt = np.linspace(0, 180, 50)
psi = rot
eulers = np.column_stack([rot, tilt, psi])
rotation_matrices = euler2matrix(eulers, axes='zyz', intrinsic=True, right_handed_rotation=True)


def test_orientationblock_instantiation():
    block = OrientationBlock(data=rotation_matrices)
    assert isinstance(block, OrientationBlock)
