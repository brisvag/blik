import numpy as np
import mrcfile

from blik.functions import peep
from blik.datablocks import PointBlock
from blik.peeper import Peeper


def test_peep_peeper():
    peeper = peep(Peeper())
    assert isinstance(peeper, Peeper)
    assert len(peeper) == 0


def test_peep_datablock():
    peeper = peep(PointBlock(data=()))
    assert isinstance(peeper, Peeper)
    assert len(peeper) == 1
    peeper = peep([PointBlock(data=()), PointBlock(data=())])
    assert isinstance(peeper, Peeper)
    assert len(peeper) == 2


def test_peep_path(tmp_path):
    mrc_path = str(tmp_path / 'test.mrc')
    mrcfile.new(mrc_path, np.random.rand(10, 10, 10).astype(np.float32))
    peeper = peep(mrc_path)
    assert isinstance(peeper, Peeper)
