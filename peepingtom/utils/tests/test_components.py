import numpy as np
from numpy.testing import assert_array_almost_equal

from ..components import ArrayContainer


def test_array_container():
    data = [1, 2, 3]
    # Instantiate
    a = ArrayContainer(data)
    assert isinstance(a, ArrayContainer)

    # Check ufuncs work properly
    b = a + 1
    assert_array_almost_equal(b, [2, 3, 4])
    b = a * 2
    assert_array_almost_equal(b, [2, 4, 6])

    # Instantiate with shape
    a = ArrayContainer(data, shape=(-1, 3))
    assert a.shape == (1, 3)

    # Check sliced views into array containers retain class
    view = a[0]
    assert isinstance(view, ArrayContainer)

    # Instantiate with dtype
    a = ArrayContainer(data, dtype=np.float32)
    assert a.dtype == np.float32
