import numpy as np
from numpy.testing import assert_array_equal, assert_array_almost_equal

from peepingtom.core import DipoleBlock

test_centers = np.asarray([[0, 0, 0],
                           [1, 1, 1],
                           [2, 2, 2]])

test_vectors = np.asarray([[0, 0, 1], [0, 0, 2], [3, 3, 3]])

test_vector_norms = np.expand_dims(np.linalg.norm(test_vectors, axis=1), axis=-1)
normalised_test_vectors = test_vectors / test_vector_norms

test_endpoints = test_centers + test_vectors


def test_dipoleblock_instantiation():
    block = DipoleBlock(test_centers, test_endpoints)
    assert isinstance(block, DipoleBlock)


def test_dipoleblock_orientation_vectors():
    block = DipoleBlock(test_centers, test_endpoints)
    assert_array_equal(block.orientation_vectors, test_vectors)


def test_dipoleblock_normalised_orientation_vector():
    block = DipoleBlock(test_centers, test_endpoints)
    assert_array_almost_equal(block.normalised_orientation_vectors, normalised_test_vectors)


def test_dipoleblock_rotation_matrices():
    block = DipoleBlock(test_centers, test_endpoints)

    # calculate rotation matrices to align test vector to each dipole in block
    vector_to_align = np.array([0, 2, 1]).reshape(1, 3, 1)
    rotation_matrices = block.calculate_orientation_block(vector_to_align)

    # calculate vector to aligns new position after rotation by rotation_matrix
    aligned_vectors = rotation_matrices @ vector_to_align
    aligned_vectors = aligned_vectors.reshape(-1, 3)

    # calculate normalised aligned vectors for comparison with dipoleblock vectors
    aligned_vectors_norm = np.linalg.norm(aligned_vectors, axis=1)
    normalised_aligned_vectors = aligned_vectors / np.expand_dims(aligned_vectors_norm, axis=-1)

    # check normalised aligned vectors match normalised dipoleblock vectors
    assert_array_almost_equal(normalised_aligned_vectors, block.normalised_orientation_vectors)
