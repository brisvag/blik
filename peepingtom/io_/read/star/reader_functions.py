"""This module contains various reader functions for parsing data from different types of STAR
files.

Each function should attempt to raise a ValueError quickly if it's not the right function
for reading a given file.

raw data is the dictionary produced by starfile.read()
"""
from .utils import rln30_df_to_particleblocks, rln31_df_to_particleblocks


def parse_relion30_3d(raw_data):
    """Attempt to parse raw data dict from starfile.read as a RELION 3.0 style star file
    """
    if len(raw_data.values()) > 1:
        raise ValueError("Cannot parse as RELION 3.0 format STAR file")

    df = list(raw_data.values())[0]
    return rln30_df_to_particleblocks(df)


def parse_rellon31_3d(raw_data):
    """Attempt to parse raw data from starfile.read as a RELION 3.1 style star file
    """
    if list(raw_data.keys()) != ['optics', 'particles']:
        raise ValueError("Cannot parse as RELION 3.1 format STAR file")

    df = raw_data['particles'].merge(raw_data['optics'])
    return rln31_df_to_particleblocks(df)


reader_functions = {'relion_3.0_3d': parse_relion30_3d,
                    'relion_3.1_3d': parse_rellon31_3d}
