from pytest import raises

from blik.datablocks.abstractblocks.datablock import DataBlock


def test_datablock():
    db = DataBlock()

    with raises(ValueError):
        db.init_depictor()
