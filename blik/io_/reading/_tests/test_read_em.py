import numpy as np
import emfile

from blik.io_.reading.em import read_em
from blik.datablocks import ImageBlock


def test_read_em(tmp_path):
    file_path = tmp_path / 'test.em'
    emfile.write(str(file_path), np.ones((3, 3, 3)))
    imageblock = read_em(file_path)
    assert isinstance(imageblock, ImageBlock)
    assert imageblock.data.shape == (3, 3, 3)
