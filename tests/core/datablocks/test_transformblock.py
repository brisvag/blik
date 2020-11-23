import numpy as np

from peepingtom.core import TransformBlock, DipoleBlock, PointBlock, ParticleBlock
from tests.test_data.blocks import particleblock

# test transform
shifts = [
    [-1, 0, 0],
    [-1, 0, 1],
    [-1, 0, -1],
    [-1, 1, 0],
    [-1, -1, 0],
    [0, 0, 0],
    [-2, 0, 0]
]
test_shifts = PointBlock(np.asarray(shifts))

test_endpoints = PointBlock(np.zeros((test_shifts.data.shape[0], 3)))
test_orientations = DipoleBlock(test_shifts, test_endpoints).calculate_orientation_block([0, 0, 1])


def test_transformblock_instantiation():
    # test that block instantiates properly
    block = TransformBlock(test_shifts, test_orientations, {})
    assert isinstance(block, TransformBlock)


def test_transformblock_application():
    block = TransformBlock(test_shifts, test_orientations, {})

    # apply transformations in block on particles
    new_block = block.apply_on(particleblock)

    # check that object returned is ParticleBlock
    assert isinstance(new_block, ParticleBlock)

    # check that no. of new particles = number of transformations * number of particles
    n_transforms = block.positions.data.shape[0]
    n_particles = particleblock.positions.data.shape[0]
    n_transformed_particles = new_block.positions.data.shape[0]

    assert n_transformed_particles == n_transforms * n_particles
