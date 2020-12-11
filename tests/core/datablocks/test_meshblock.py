import numpy as np

from peepingtom.core import MeshBlock

vertices = np.array([[0, 0, 0],
                     [0, 0, 1],
                     [0, 1, 0],
                     [1, 0, 0],
                     [0, 1, 1],
                     [1, 0, 1],
                     [1, 1, 0],
                     [1, 1, 1]])

faces = np.array([[0, 3, 4],
                  [7, 3, 4],
                  [0, 1, 4],
                  [0, 5, 7],
                  [3, 6, 5]
                  ])


def test_meshblock_instantiation():
    # check that meshblock can be instantiated properly
    block = MeshBlock(vertices, faces)
    assert isinstance(block, MeshBlock)
    assert hasattr(block, 'vertices')
    assert hasattr(block, 'faces')


def test_triangles():
    block = MeshBlock(vertices, faces)
    triangles = block.triangles
    assert triangles.shape[0] == faces.shape[0]
    assert triangles.shape[2] == 3


def test_midpoints():
    block = MeshBlock(vertices, faces)
    midpoints = block.midpoints
    assert midpoints.shape == (faces.shape[0], 3)
