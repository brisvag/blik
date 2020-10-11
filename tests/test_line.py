import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.interpolate import splev
from numpy.testing import assert_array_almost_equal

from ntp.geometry_primitives import Line

# set up 3d point example
n_points = 80
z = np.linspace(0, 8 * np.pi, n_points)
x = np.sin(z) + np.random.normal(size=n_points) * 0.05 + np.linspace(-2, 2, n_points)
y = np.cos(z) + np.random.normal(size=n_points) * 0.1 + np.linspace(-0.5, 3, n_points)

points = np.column_stack([x, y, z])


def test_line_instantiation():
    line = Line()
    assert isinstance(line, Line)


line = Line()


def test_points():
    line.points = points
    assert line.points.shape[0] == n_points
    assert line.points.shape[1] == 3


line.points = points


def test_xyz():
    line.points = points
    assert_array_almost_equal(line.x, x)
    assert_array_almost_equal(line.y, y)
    assert_array_almost_equal(line.z, z)


def test_spline_fit():
    tck, u = line._fit_spline()


def test_n_points():
    assert line.n_points == n_points


def test__calculate_smooth_backbone():
    line._calculate_smooth_backbone(1000)
