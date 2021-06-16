import numpy as np

from blik.io_.writing.star import write_star
from blik.datablocks import ParticleBlock


def test_write_star(tmp_path):
    file_path = tmp_path / 'test.star'
    particleblock = ParticleBlock(positions_data=np.ones((2, 3)),
                                  orientations_data=np.ones((2, 3, 3)),
                                  properties_data={'a': np.ones((2,))})

    write_star(particleblock, file_path)
