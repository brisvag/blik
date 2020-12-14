import numpy as np
import mrcfile

from peepingtom.io_.read.mrc import read_mrc
from peepingtom.core import ImageBlock


def test_read_mrc(tmp_path):
    file_path = tmp_path / 'TS_00.mrc'
    mrcfile.new(str(file_path), np.ones((3,3,3), dtype=np.float32))
    imageblock = read_mrc(file_path)
    assert isinstance(imageblock, ImageBlock)
    assert imageblock.data.shape == (3,3,3)
    assert imageblock.name == 'TS_00'
