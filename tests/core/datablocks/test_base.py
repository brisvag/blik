"""
Tests for DataBlock objects
"""

import pytest

from peepingtom.core import DataBlock, MultiBlock, DataCrate, Model
from ...test_data.blocks import pointblock, lineblock, orientationblock


def test_datablock():
    # assert that DataBlock class cannot be instantiated directly
    with pytest.raises(NotImplementedError):
        DataBlock([])

    # assert that subclassing and implementing _data_setter works
    class SubBlock(DataBlock):
        def __init__(self, data, **kwargs):
            super().__init__(data, **kwargs)

        def _data_setter(self, data):
            return data

    subblock = SubBlock([])
    assert isinstance(subblock, (DataBlock, SubBlock))

    # assert that subclass has parent attribute
    assert hasattr(subblock, 'parent')

    # assert that subclassing and not implementing _data_setter fails on subclass instantiation
    class SubBlock(DataBlock):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)

    with pytest.raises(TypeError):
        subblock = SubBlock()


def test_multiblock():
    block = MultiBlock()
    assert isinstance(block, MultiBlock)


def test_datacrate():
    # assert that datacrate instantiates properly
    crate = DataCrate([pointblock, lineblock, orientationblock])
    assert isinstance(crate, DataCrate)


def test_model():
    # assert that Model class cannot be instantiated directly
    with pytest.raises(TypeError):
        Model()
