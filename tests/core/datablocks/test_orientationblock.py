import numpy as np
from numpy.testing import assert_array_equal
from eulerangles import euler2matrix

from peepingtom.core.datablocks import OrientationBlock

# test data for orientationblock
# orientations
rot = np.zeros(50)
tilt = np.linspace(0, 180, 50)
psi = rot
eulers = np.column_stack([rot, tilt, psi])
rotation_matrices = euler2matrix(eulers, axes='zyz', intrinsic=True, positive_ccw=True)


def test_orientationblock_instantiation():
    block = OrientationBlock(rotation_matrices)
    assert isinstance(block, OrientationBlock)


def test_orientationblock_unit_vectors():
    block = OrientationBlock(rotation_matrices)
    x = block._unit_vector('x')
    y = block._unit_vector('y')
    z = block._unit_vector('z')

    unit_x = np.asarray([1, 0, 0]).reshape(3, 1)
    unit_y = np.asarray([0, 1, 0]).reshape(3, 1)
    unit_z = np.asarray([0, 0, 1]).reshape(3, 1)

    assert_array_equal(x, unit_x)
    assert_array_equal(y, unit_y)
    assert_array_equal(z, unit_z)
