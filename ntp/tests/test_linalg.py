import numpy as np
from numpy.testing import assert_array_almost_equal

import ntp.linalg


def test_normalise():
    # test 1d
    a = np.array([0.2, 0.2, 0.2])
    b = ntp.linalg.normalise(a)
    assert_array_almost_equal(np.linalg.norm(b), 1)

    # test 2d without explicit axis spec, expect normalisation along last axis
    a = a.reshape(-1, 3)
    b = ntp.linalg.normalise(a)
    assert_array_almost_equal(np.linalg.norm(b, axis=1), 1)

    # test 3d with explicit axis spec, expect normalisation along axis 1
    a = a.reshape(-1, 3, 1)
    b = ntp.linalg.normalise(b, axis=1)
    assert_array_almost_equal(np.linalg.norm(b, axis=1), 1)


def test_align():
    # initialise vectors
    size = (1000000, 3, 1)
    a = np.random.normal(size=size)
    a /= np.linalg.norm(a, axis=1).reshape(-1, 1, 1)
    b = np.random.normal(size=size)
    b /= np.linalg.norm(b, axis=1).reshape(-1, 1, 1)

    # calculate rotation matrices
    r = ntp.linalg.align(a, b)

    # calculate transformed vector a
    r_a = r @ a

    # calculate normalised transformed a for comparison with b
    r_a_n = ntp.linalg.normalise(r_a, axis=1)

    assert_array_almost_equal(r_a_n, b, decimal=3)


