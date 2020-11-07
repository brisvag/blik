from ..geometric_primitives import Point2D

def test_point2d():
    data = [1, 2]

    # test instantiation
    p = Point2D(data)
    assert isinstance(p, Point2D)
    assert p.shape == (2, )

    # check reshaping is working as expected
    data = [[1, 2]]
    p = Point2D(data)
    assert p.shape == (2, )

    # check has parent attribute from Child class
    assert hasattr(p, 'parent')