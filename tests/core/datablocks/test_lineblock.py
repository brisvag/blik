import numpy as np

from peepingtom.core.datablocks import LineBlock

# test data for lineblock
v = np.linspace(0, 12)
line_2d = np.column_stack([v, np.sin(v)])
line_3d = np.column_stack([v, np.sin(v), np.cos(v)])


def test_lineblock_instantiation():
    # test LineBlock instantiation
    LineBlock(line_2d)
    LineBlock(line_3d)


def test_lineblock_fit_spline():
    # test LineBlock.fit_spline
    block = LineBlock(line_3d)
    tck = block.fit_spline('xyz')

    assert block._tck is not None
    assert isinstance(tck, list)


def test_lineblock_evaluate_spline():
    # test LineBlock.evaluate_spline
    block = LineBlock(line_3d)
    block.fit_spline('xyz')
    for n in [10, 100, 1000]:
        spline = block.evaluate_spline(n)
        assert isinstance(spline, np.ndarray)

    assert block._tck is not None
    assert isinstance(block._tck, list)
