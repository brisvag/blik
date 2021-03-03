import dynamotable

from .utils import euler2matrix_dynamo, name_from_volume
from ....datablocks import ParticleBlock


def read_tbl(table_path, table_map_file=None, regex_name=None):
    """Reads a dynamo format table file into a list of ParticleBlocks
    """
    df = dynamotable.read(table_path, table_map_file)

    coord_headings = ['x', 'y', 'z']
    shift_headings = ['dx', 'dy', 'dz']
    euler_headings = ['tdrot', 'tilt', 'narot']

    split_on = 'tomo'
    if 'tomo_file' in df.columns:
        split_on = 'tomo_file'

    particleblocks = []

    for volume, df_ in df.groupby(split_on):
        name = name_from_volume(volume, regex_name)
        xyz = (df_[coord_headings] + df_[shift_headings]).to_numpy()
        eulers = df_[euler_headings]
        rotation_matrices = euler2matrix_dynamo(eulers)
        properties = {key: df_[key].to_numpy() for key in df.columns}

        particleblocks.append(ParticleBlock(xyz, rotation_matrices, properties, name=name))

    return particleblocks
