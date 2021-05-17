import numpy as np
import pandas as pd
import mrcfile
import starfile

from peepingtom.io_.reading.main import read


def test_read(tmp_path):
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

    p = read(tmp_path / '*', name_regex=r'test\d')

    assert len(p) == 4
    assert len(p.volumes) == 2
