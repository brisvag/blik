from ntp.geometry_primitives import Mesh

import numpy as np
from numpy.testing import assert_array_almost_equal

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


def test_surface_area():
    assert False
