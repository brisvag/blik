import numpy as np

from ..utils import guess_name
from ...datablocks import ParticleBlock


def read_box(box_path, name_regex=None, pixel_size=1, **kwargs):
    data = np.loadtxt(box_path)
    orientations = np.tile(np.identity(3), (len(data), 1, 1))
    name = guess_name(box_path, name_regex)
    return ParticleBlock(data, orientations, name=name, pixel_size=pixel_size)
