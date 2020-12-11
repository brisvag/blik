import starfile
import eulerangles

from ....core import ParticleBlock
from ...utils import star_types, guess_name


def split_and_name(dataframe, split_by, basename, name_regex=None):
    """
    splits a dataframe from a starfile in separate
    """
    if split_by in dataframe.columns:
        groups = dataframe.groupby('rlnMicrographName')
        return [(guess_name(subname, name_regex), dataframe) for subname, dataframe in groups]
    else:
        return [(guess_name(basename, name_regex), dataframe)]


def euler2matrix(euler_angles, convention):
    """
    convert euler angles to matrices
    """
    rotation_matrices = eulerangles.euler2matrix(euler_angles,
                                                 axes=convention['axes'],
                                                 intrinsic=convention['intrinsic'],
                                                 positive_ccw=convention['positive_ccw'])

    # If rotation matrices represent rotations of particle onto reference
    # invert them so that we return matrices which transform reference onto particle
    if convention['rotate_reference'] is False:
        rotation_matrices = rotation_matrices.transpose((0, 2, 1))
    return rotation_matrices


def read_star(star_path, data_columns=[], name_regex=None, **kwargs):
    """
    read a starfile into one or multiple ParticleBlocks
    data_columns: a list of column names to include as properties
    name_regex: a regex pattern to use to guess the name of individual datasets
    """
    raw_dfs = starfile.read((star_path), always_dict=True)

    # metadata = {}
    dataframes = []
    # check if relion3.1 format
    if list(raw_dfs.keys()) == ['optics', 'particles']:
        # TODO: use optics metadata
        # metadata = raw_dfs['optics']
        dataframes.append(raw_dfs['particles'])
    else:
        # assume every key is a different dataset (older version)
        # TODO: make more specific
        dataframes.extend(list(raw_dfs.values()))

    # create particles
    datablocks = []
    for dataframe in dataframes:
        # try every type of starfile convention
        for star_type, params in star_types.items():
            # check if the necessary columns exist
            if all(colname in dataframe.columns for colname in params['coords']):
                # split and guess names
                named_dfs = split_and_name(dataframe, split_by=params['split_by'],
                                           basename=star_path, name_regex=name_regex)
                for name, df in named_dfs:
                    # extract the data and convert it to peepingtom format
                    raw_positions = df[params['coords']]
                    raw_shifts = df.get(params['shifts'], 0)
                    raw_eulers = df[params['angles']]
                    raw_properties = df[data_columns]

                    positions = (raw_positions + raw_shifts).to_numpy()
                    orientations = euler2matrix(raw_eulers, params['angle_convention'])
                    properties = {key: df[key].to_numpy() for key in raw_properties}

                    datablocks.append(ParticleBlock(positions, orientations, properties, name=name))
                # break of out loop if something was found
                break
        else:
            raise ValueError(f'dataframe with columns {list(dataframe.columns)} could not be read')

    return datablocks
