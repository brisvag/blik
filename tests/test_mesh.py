from ntp.mesh import Mesh

import numpy as np

vertices = np.asarray([[0, 0, 0],
                       [0, 1, 0],
                       [1, 0, 0],
                       [1, 1, 0]])
faces = np.asarray([[0, 1, 2],
                    [3, 1, 2]])

mesh = Mesh(vertices=vertices, faces=faces)


def test_triangles():
    triangles = mesh.triangles
    assert triangles.shape[0] == faces.shape[0]
    assert triangles.shape[-2:] == (3, 3)


def test_ab():
    assert mesh.AB.shape[0] == faces.shape[0]
