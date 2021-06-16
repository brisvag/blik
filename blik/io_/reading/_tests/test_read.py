import numpy as np
import pandas as pd
import mrcfile
import starfile

from blik.io_.reading.main import read
from blik.dataset import DataSet
from blik.datablocks import PointBlock


def test_read_path(tmp_path):
    # mrc file
    mrc_path1 = tmp_path / 'test1.mrc'
    mrc_path2 = tmp_path / 'test2.mrc'
    mrcfile.new(str(mrc_path1), np.ones((3, 3), dtype=np.float32))
    mrcfile.new(str(mrc_path2), np.ones((3, 3), dtype=np.float32))

    # star file
    df = pd.DataFrame({
        'rlnCoordinateX': [1, 2],
        'rlnCoordinateY': [1, 2],
        'rlnCoordinateZ': [1, 2],
        'rlnOriginX': [1, 2],
        'rlnOriginY': [1, 2],
        'rlnOriginZ': [1, 2],
        'rlnAngleRot': [1, 2],
        'rlnAngleTilt': [1, 2],
        'rlnAnglePsi': [1, 2],
        'rlnMicrographName': ['test1', 'test2'],
    })
    star_path = tmp_path / 'test.star'
    starfile.new(df, star_path)

    dataset = read(tmp_path / '*', name_regex=r'test\d')

    assert len(dataset) == 4
    assert len(dataset.volumes) == 2


def test_read_dataset():
    dataset = read(DataSet())
    assert isinstance(dataset, DataSet)
    assert len(dataset) == 0


def test_read_datablock():
    dataset = read(PointBlock(data=()))
    assert isinstance(dataset, DataSet)
    assert len(dataset) == 1
    dataset = read([PointBlock(data=()), PointBlock(data=())])
    assert isinstance(dataset, DataSet)
    assert len(dataset) == 2
