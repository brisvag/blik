"""
Tests for DataBlock objects
"""

import pytest
import numpy as np
from eulerangles import euler2matrix
from numpy.testing import assert_array_equal

from peepingtom.core import DataBlock, PointBlock, LineBlock, OrientationBlock


def test_datablock():
    # assert that DataBlock class cannot be instantiated directly
    with pytest.raises(TypeError):
        block = DataBlock()

    # assert that subclassing and implementing _data_setter works
    class SubBlock(DataBlock):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)

        def _data_setter(self, data):
            return data

    subblock = SubBlock()
    assert isinstance(subblock, (DataBlock, SubBlock))

    # assert that subclass has parent attribute
    assert hasattr(subblock, 'parent')

    # assert that subclassing and not implementing _data_setter fails on subclass instantiation
    class SubBlock(DataBlock):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)

    with pytest.raises(TypeError):
        subblock = SubBlock()


# test data pointblock
single_point_2d = [1, 2]
points_2d = [[1, 2], [3, 4]]

single_point_3d = [1, 2, 3]
points_3d = [[1, 2, 3], [4, 5, 6]]

point_nd = np.arange(48).reshape(6, 8)


def test_pointblock_instantiation():
    # test instantiation for 2d, 3d and nd points
    block = PointBlock(single_point_2d)
    block = PointBlock(points_2d)
    block = PointBlock(single_point_3d)
    block = PointBlock(points_3d)
    block = PointBlock(point_nd)

def test_pointblock_xyz():
    # test 'x', 'y' and 'z' properties
    block = PointBlock(single_point_2d)
    assert_array_equal(block.x, [1])
    assert_array_equal(block.y, [2])

    block = PointBlock(single_point_3d)
    assert_array_equal(block.x, [1])
    assert_array_equal(block.y, [2])
    assert_array_equal(block.z, [3])


def test_pointblock_get_named_dimension():
    # test _get_named_dimension method
    block = PointBlock(single_point_3d)

    # check output is array
    x = block._get_named_dimension('x')
    assert isinstance(x, np.ndarray)

    # try with multiple named dims
    xyz = block._get_named_dimension('xyz')
    assert isinstance(xyz, np.ndarray)
    assert xyz.shape == (1, 3)

    xyz = block._get_named_dimension('xyz', as_type='tuple')
    assert isinstance(xyz, tuple)
    assert len(xyz) == 3


def test_pointblock_center_of_mass():
    # test center_of_mass property
    # single point case
    block = PointBlock(single_point_3d)
    assert_array_equal(block.center_of_mass, single_point_3d)

    # multi point case
    block = PointBlock(points_3d)
    assert_array_equal(block.center_of_mass, [2.5, 3.5, 4.5])


def test_pointblock_distance_to():
    # test distance_to method
    block = PointBlock(single_point_3d)

    assert block.distance_to([1, 2, 3]) == 0
    assert block.distance_to([2, 3, 4]) == np.sqrt(3)

    # check for failure
    with pytest.raises(ValueError):
        block.distance_to([1, 2, 3, 4, 5, 6])


# test data for lineblock
v = np.linspace(0, 12)
line_2d = np.column_stack([v, np.sin(v)])
line_3d = np.column_stack([v, np.sin(v), np.cos(v)])


def test_lineblock_instantiation():
    # test LineBlock instantiation
    block = LineBlock(line_2d)
    block = LineBlock(line_3d)


def test_lineblock_fit_spline():
    # test LineBlock.fit_spline
    block = LineBlock(line_3d)
    tck = block.fit_spline('xyz')

    assert block._tck is not None
    assert isinstance(tck, list)


def test_lineblock_evaluate_spline():
    # test LineBlock.fit_spline
    block = LineBlock(line_3d)
    block.fit_spline('xyz')
    for n in [10, 100, 1000]:
        spline = block.evaluate_spline(n)
        assert isinstance(spline, np.ndarray)

    assert block._tck is not None
    assert isinstance(block._tck, list)



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


# test data for ParticleBlock
# positions
z = np.linspace(0, 6*np.pi, 50)
x = 3 * np.sin(z)
y = 3 * np.cos(z)
xyz = np.column_stack([x, y, z])
