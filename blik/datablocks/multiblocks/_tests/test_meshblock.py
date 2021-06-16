import numpy as np

from blik.datablocks.multiblocks.meshblock import MeshBlock

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
    block = MeshBlock(vertices_data=vertices, faces_data=faces)
    assert isinstance(block, MeshBlock)
    assert hasattr(block, 'vertices')
    assert hasattr(block, 'faces')


def test_triangles():
    block = MeshBlock(vertices_data=vertices, faces_data=faces)
    triangles = block.triangles
    assert len(triangles) == len(faces)
    assert triangles.shape[-1] == 3


def test_midpoints():
    block = MeshBlock(vertices_data=vertices, faces_data=faces)
    midpoints = block.midpoints
    assert midpoints.shape == (faces.shape[0], 3)
