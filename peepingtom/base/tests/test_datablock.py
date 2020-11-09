"""
Tests for DataBlock objects
"""
import pytest

from ..datablock import DataBlock


def test_datablock():
    # assert that DataBlock class cannot be instantiated directly
    with pytest.raises(TypeError):
        block = DataBlock()

    # assert that subclassing and implementing _data_setter works
    class SubBlock(DataBlock):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)

        def _data_setter(self, data):
            return data

    subblock = SubBlock()
    assert isinstance(subblock, (DataBlock, SubBlock))

    # assert that subclass has parent attribute
    assert hasattr(subblock, 'parent')

    # assert that subclassing and not implementing _data_setter fails on subclass instantiation
    class SubBlock(DataBlock):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)

    with pytest.raises(TypeError):
        subblock = SubBlock()


def test_pointblock():
    # test data
    points_2d = [[1, 2], [3, 4]]