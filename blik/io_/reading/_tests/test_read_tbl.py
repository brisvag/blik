import pandas as pd
import dynamotable

from blik.io_.reading.tbl import read_tbl
from blik.datablocks import ParticleBlock


def test_read_tbl(tmp_path):
    df = pd.DataFrame({
        'x': [1, 2],
        'y': [1, 2],
        'z': [1, 2],
        'dx': [1, 2],
        'dy': [1, 2],
        'dz': [1, 2],
        'tdrot': [1, 2],
        'tilt': [1, 2],
        'narot': [1, 2],
        'tomo': [1, 2],
    })
    file_path = tmp_path / 'test.tbl'
    dynamotable.write(df, file_path)

    particleblocks = read_tbl(file_path)
    assert all(isinstance(pb, ParticleBlock) for pb in particleblocks)
