import numpy as np
import starfile

from ..utils import guess_name
from ...datablocks import ParticleBlock


def read_cbox(cbox_path, name_regex=None, pixel_size=None, **kwargs):
    data = starfile.read(cbox_path)['cryolo']
    coords = data[[f'Coordinate{axis}' for axis in 'XYZ']].to_numpy()
    orientations = np.tile(np.identity(3), (len(data), 1, 1))
    name = guess_name(cbox_path, name_regex)
    return ParticleBlock(coords, orientations, name=name, pixel_size=pixel_size)
