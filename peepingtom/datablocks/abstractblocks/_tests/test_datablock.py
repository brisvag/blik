from pytest import raises

from peepingtom.datablocks.abstractblocks.datablock import DataBlock


def test_datablock():
    db = DataBlock()

    with raises(ValueError):
        db.init_depictor()
