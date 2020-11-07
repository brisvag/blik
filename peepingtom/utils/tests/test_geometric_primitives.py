import numpy as np
from numpy.testing import assert_almost_equal, assert_array_equal

from ..geometric_primitives import Point2D, Points2D, Point3D, Points3D


def test_point2d():
    data = [1, 2]

    # test instantiation
    p = Point2D(data)
    assert isinstance(p, Point2D)

    # check dimensionality and shape
    assert p.ndim == 1
    assert p.shape == (2,)

    # check has parent attribute from Child class
    assert hasattr(p, 'parent')

    # check has attributes 'x' and 'y'
    assert hasattr(p, 'x')
    assert hasattr(p, 'y')

    # check attributes 'x' and 'y' are correct
    assert p.x == 1
    assert p.y == 2

    # check reshaping is working as expected
    data = [[1, 2]]
    p = Point2D(data)
    assert p.shape == (2,)

    # check that distance_to method works
    distance = Point2D([0, 0]).distance_to_point([1, 1])
    assert_almost_equal(np.sqrt(2), distance, decimal=7)

    # check center of mass
    assert_array_equal(p.center_of_mass, p)
    assert p.center_of_mass.ndim == 1


def test_points2d():
    data = np.arange(4).reshape(2, 2)

    # test instantiation
    p = Points2D(data)
    assert isinstance(p, Points2D)

    # check dimensionality and shape
    assert p.ndim == 2
    assert p.shape == (2, 2)

    # check center of mass
    assert_array_equal(p.center_of_mass, [1, 2])

    # check distance to
    assert_almost_equal(p.distance_to_point([1, 2]), 0)

    # check has attributes
    assert hasattr(p, 'x')
    assert hasattr(p, 'y')

    assert_array_equal(p.x, [0, 2])
    assert_array_equal(p.y, [1, 3])

    assert hasattr(p, 'parent')

    # check reshaping works correctly
    data = np.arange(2)
    p = Points2D(data)
    assert p.ndim == 2
    assert p.shape == (1, 2)


def test_point3d():
    data = [1, 2, 3]

    # test instantiation
    p = Point3D(data)
    assert isinstance(p, Point3D)

    # check dimensionality and shape
    assert p.ndim == 1
    assert p.shape == (3,)

    # check has parent attribute from Child class
    assert hasattr(p, 'parent')

    # check has attributes 'x', 'y' and 'z'
    assert hasattr(p, 'x')
    assert hasattr(p, 'y')
    assert hasattr(p, 'z')

    # check attributes 'x' and 'y' are correct
    assert p.x == 1
    assert p.y == 2
    assert p.z == 3

    # check reshaping is working as expected
    data = [[1, 2, 3]]
    p = Point3D(data)
    assert p.shape == (3,)

    # check that distance_to method works
    distance = Point3D([0, 0, 0]).distance_to_point([1, 1, 1])
    assert_almost_equal(np.sqrt(3), distance, decimal=7)

    # check center of mass
    assert_array_equal(p.center_of_mass, p)
    assert p.center_of_mass.ndim == 1


def test_points3d():
    data = np.arange(9).reshape(3, 3)

    # test instantiation
    p = Points3D(data)
    assert isinstance(p, Points3D)

    # check dimensionality and shape
    assert p.ndim == 2
    assert p.shape == (3, 3)

    # check center of mass
    assert_array_equal(p.center_of_mass, [3, 4, 5])

    # check distance to
    assert_almost_equal(p.distance_to_point([3, 4, 5]), 0)

    # check has attributes
    assert hasattr(p, 'x')
    assert hasattr(p, 'y')
    assert hasattr(p, 'z')

    assert_array_equal(p.x, [0, 3, 6])
    assert_array_equal(p.y, [1, 4, 7])
    assert_array_equal(p.z, [2, 5, 8])

    assert hasattr(p, 'parent')

    # check reshaping works correctly
    data = np.arange(3)
    p = Points3D(data)
    assert p.ndim == 2
    assert p.shape == (1, 3)