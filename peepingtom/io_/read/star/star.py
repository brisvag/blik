import re

import starfile

from ....core import ParticleBlock
from .constants import star_types
from ...utils import EulerAngleHelper


# a list of commonly used base names for starfiles in regex form
common_name_regexes = (
    'TS_\d+',
)


def guess_name(string, name_regex=None):
    """
    guess an appropriate name based on the input path or string
    """
    possible_names = list(common_name_regexes)
    if name_regex is not None:
        possible_names.insert(0, name_regex)

    for name in possible_names:
        if match := re.search(name, str(string)):
            return match.group(0)
    return 'NoName'


def split_and_name(dataframe, split_by, basename, name_regex=None):
    """
    splits a dataframe from a starfile in separate
    """
    if split_by in dataframe.columns:
        groups = dataframe.groupby('rlnMicrographName')
        return [(guess_name(subname, name_regex), dataframe) for subname, dataframe in groups]
    else:
        return [(guess_name(basename, name_regex), dataframe)]



def read_star(star_path, data_columns, name_regex=None):
    """
    read a starfile into one or multiple ParticleBlocks
    data_columns: a list of column names to include as properties
    name_regex: a regex pattern to use to guess the name of individual datasets
    """
    raw_dfs = starfile.read((star_path), always_dict=True)

    metadata = {}
    dataframes = []
    # check if relion3.1 format
    if list(raw_dfs.keys()) == ['optics', 'particles']:
        metadata.append(raw_dfs['optics'])
        dataframes.append(raw_dfs['particles'])
    else:
        # assume every key is a different dataset (older version)
        # TODO: make more specific
        dataframes.extend(list(raw_dfs.values()))

    # create particles
    # TODO: use optics metadata
    datablocks = []
    for dataframe in dataframes:
        # try every type of starfile
        for star_type, params in star_types.items():
            # check if the necessary columns exist
            if all(colname in dataframe.columns for colname in params['coords'] + params['angles']):
                # split and guess names
                named_dfs = split_and_name(dataframe, split_by=params['split_by'],
                                           basename=star_path, name_regex=name_regex)
                for name, df in named_dfs:
                    raw_positions = df[params['coords']]
                    raw_shifts = df.get(params['shifts'], 0)
                    raw_eulers = df[params['angles']]
                    raw_properties = df[data_columns]

                    positions = (raw_positions + raw_shifts).to_numpy()
                    orientations = EulerAngleHelper(raw_eulers).euler2matrix(star_type)
                    properties = {key: df[key].to_numpy() for key in df}

                    datablocks.append(ParticleBlock(positions, orientations, properties, name=name))
                # break of out loop if something was found
                break
        else:
            raise ValueError(f'dataframe with columns {list(dataframe.columns)} could not be read')

    return datablocks
