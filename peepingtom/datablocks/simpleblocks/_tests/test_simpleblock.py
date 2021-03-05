import pytest

from peepingtom.datablocks.simpleblocks.simpleblock import SimpleBlock


def test_simpleblock():
    # assert that SimpleBlock class cannot be instantiated directly
    with pytest.raises(NotImplementedError):
        SimpleBlock([])

    # assert that subclassing and implementing _data_setter works
    class SubBlock(SimpleBlock):
        def __init__(self, data, **kwargs):
            super().__init__(data, **kwargs)

        def _data_setter(self, data):
            return data

    subblock = SubBlock([])
    assert isinstance(subblock, (SimpleBlock, SubBlock))

    # assert that subclassing and not implementing _data_setter fails on subclass instantiation
    class SubBlock(SimpleBlock):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)

    with pytest.raises(NotImplementedError):
        subblock = SubBlock()
