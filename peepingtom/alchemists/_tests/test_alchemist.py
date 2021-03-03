from pytest import raises

from peepingtom.alchemists import Alchemist
from peepingtom.datablocks import DataBlock


def test_alchemist():
    db = DataBlock()
    with raises(NotImplementedError):
        alch = Alchemist(db)
