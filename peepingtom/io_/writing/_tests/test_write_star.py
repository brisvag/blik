import numpy as np

from peepingtom.io_.writing.star import write_star
from peepingtom.datablocks import ParticleBlock


def test_write_star(tmp_path):
    file_path = tmp_path / 'test.star'
    particleblock = ParticleBlock(np.ones((2, 3)), np.ones((2, 3, 3)), {'a': np.ones((2,))})

    write_star(particleblock, file_path)
