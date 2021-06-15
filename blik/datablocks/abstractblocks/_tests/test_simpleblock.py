import pytest

from blik.datablocks.abstractblocks.simpleblock import SimpleBlock


def test_simpleblock():
    # assert that SimpleBlock class cannot be instantiated directly
    with pytest.raises(TypeError):
        SimpleBlock([])

    # assert that subclassing and implementing _data_setter works
    class SubBlock(SimpleBlock):
        def _data_setter(self, data):
            return data

    subblock = SubBlock(data=())
    assert isinstance(subblock, (SimpleBlock, SubBlock))
