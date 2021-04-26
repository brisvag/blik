import numpy as np

from ...utils import guess_name
from ....datablocks import ParticleBlock


def read_box(box_path, name_regex=None):
    data = np.loadtxt(box_path)
    orientations = np.tile(np.identity(3), (100, 1, 1))
    name = guess_name(box_path, name_regex)
    return ParticleBlock(data, orientations, name=name)
