import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.interpolate import splev
from numpy.testing import assert_array_almost_equal
from ntp.geometric_primitives import Mesh, Line

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
    tck, u = line.spline


def test_n_points():
    assert line.n_points == n_points


def test_calculate_smooth_backbone():
    line._calculate_smooth_backbone(1000)

def test_calculate_backbone_delta():
    line._calculate_smooth_backbone(1000)
    line.backbone_delta
    4




# Create vertices and faces for an example mesh
vertices = np.asarray([[0, 0, 0],
                       [0, 1, 0],
                       [1, 0, 0],
                       [1, 1, 0]])
faces = np.asarray([[0, 1, 2],
                    [3, 1, 2]])


def test_mesh_instantiation():
    mesh = Mesh(vertices=vertices, faces=faces)
    assert isinstance(mesh, Mesh)
    assert isinstance(mesh.vertices, np.ndarray)
    assert isinstance(mesh.faces, np.ndarray)
    return mesh


mesh = test_mesh_instantiation()


def test_triangles():
    triangles = mesh.triangles
    assert triangles.shape[0] == mesh.faces.shape[0]
    assert triangles.shape[-2:] == (3, 3)
    assert len(triangles.shape) == 3


def test_ab():
    assert mesh.AB.shape[0] == faces.shape[0]
    assert_array_almost_equal(mesh.AB, [1., 1.])


# def test_surface_area():
#     TODO
#     assert False
