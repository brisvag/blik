import numpy as np
import pandas as pd
import dynamotable

from .utils import euler2matrix_dynamo, name_from_volume
from ...utils import rotangle2matrix
from ....datablocks import ParticleBlock


def read_tbl(table_path, table_map_file=None, name_regex=None, pixel_size=None):
    """
    Reads a dynamo format table file into a list of ParticleBlocks
    """
    df = dynamotable.read(table_path, table_map_file)

    coord_headings = ['x', 'y', 'z']
    shift_headings = ['dx', 'dy', 'dz']
    euler_headings = {3: ['tdrot', 'tilt', 'narot'], 2: 'tilt'}  # TODO: 2d column name might be wrong!

    split_on = 'tomo'
    if 'tomo_file' in df.columns:
        split_on = 'tomo_file'

    particleblocks = []

    if coord_headings[-1] in df.columns:
        dim = 3
    else:
        dim = 2
    for volume, df_volume in df.groupby(split_on):
        name = name_from_volume(volume, name_regex)
        coords = df_volume[coord_headings[:dim]].to_numpy(dtype=float)
        shifts = df_volume.get(shift_headings[:dim], pd.Series([0.0])).to_numpy()
        coords += shifts

        eulers = df_volume.get(euler_headings[dim], pd.Series([0])).to_numpy()
        if dim == 3:
            rotation_matrices = euler2matrix_dynamo(eulers)
        else:
            rotation_matrices = rotangle2matrix(eulers)

        properties = {key: df_volume[key].to_numpy() for key in df.columns}

        if pixel_size is None:
            pixel_size = np.array([1] * dim)

        particleblocks.append(ParticleBlock(coords, rotation_matrices, properties, pixel_size=pixel_size, name=name))

    return particleblocks
