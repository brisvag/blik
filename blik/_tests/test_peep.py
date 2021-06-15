import numpy as np
import mrcfile

from blik.functions import peep
from blik.datablocks import PointBlock
from blik.dataset import DataSet


def test_peep_dataset():
    dataset = peep(DataSet())
    assert isinstance(dataset, DataSet)
    assert len(dataset) == 0


def test_peep_datablock():
    dataset = peep(PointBlock(data=()))
    assert isinstance(dataset, DataSet)
    assert len(dataset) == 1
    dataset = peep([PointBlock(data=()), PointBlock(data=())])
    assert isinstance(dataset, DataSet)
    assert len(dataset) == 2


def test_peep_path(tmp_path):
    mrc_path = str(tmp_path / 'test.mrc')
    mrcfile.new(mrc_path, np.random.rand(10, 10, 10).astype(np.float32))
    dataset = peep(mrc_path)
    assert isinstance(dataset, DataSet)
