"""This module contains various reader functions for parsing data from different types of STAR
files.

Each function should attempt to raise a ParseError quickly if it's not the right function
for reading a given file.

raw data is the dictionary produced by starfile.read()
"""
import numpy as np
import pandas as pd
import eulerangles

from ...utils import guess_name, ParseError, rotangle2matrix
from ....datablocks import ParticleBlock


coord_headings = [f'rlnCoordinate{axis}' for axis in 'XYZ']
euler_headings = {
    3: [f'rlnAngle{angle}' for angle in ('Rot', 'Tilt', 'Psi')],
    2: 'rlnAnglePsi'
}
shift_headings = {
    '3.0': [f'rlnOrigin{axis}' for axis in 'XYZ'],
    '3.1': [f'rlnOrigin{axis}Angst' for axis in 'XYZ']
}

pixel_size_headings = {
    '3.0': ['rlnPixelSize'],
    '3.1': ['rlnImagePixelSize']
}
micrograph_name_heading = 'rlnMicrographName'


def extract_data(df, mode='3.1', name_regex=None):
    particleblocks = []
    if coord_headings[-1] in df.columns:
        dim = 3
    else:
        dim = 2
    for micrograph_name, df_volume in df.groupby('rlnMicrographName'):

        name = guess_name(micrograph_name, name_regex)

        coords = df_volume[coord_headings[:dim]].to_numpy(dtype=float)
        shifts = df_volume.get(shift_headings[mode][:dim], pd.Series([0.0])).to_numpy()
        px_size = df_volume.get(pixel_size_headings[mode], pd.Series([1.0])).to_numpy()
        # only relion 3.1 has shifts in angstroms
        if mode == '3.1':
            shifts = shifts / px_size
        coords += shifts

        eulers = df_volume.get(euler_headings[dim], pd.Series([0])).to_numpy()
        if dim == 3:
            rotation_matrices = euler2matrix(eulers)
        else:
            rotation_matrices = rotangle2matrix(eulers)

        properties = {key: df_volume[key].to_numpy() for key in df.columns}

        # TODO: better way to handle pizel size? Now we can only account for uniform size
        pixel_size = px_size.flatten()[0]
        if dim == '3d':
            pixel_size = [pixel_size] * 3
        else:
            pixel_size = [pixel_size] * 2
        particleblocks.append(ParticleBlock(coords, rotation_matrices, properties, pixel_size=np.array(pixel_size), name=name))

    return particleblocks


def euler2matrix(euler_angles):
    """
    Convert (n, 3) array of RELION euler angles to rotation matrices
    Resulting rotation matrices rotate references into particles
    """
    rotation_matrices = eulerangles.euler2matrix(euler_angles,
                                                 axes='zyz',
                                                 intrinsic=True,
                                                 right_handed_rotation=True)

    rotation_matrices = rotation_matrices.swapaxes(-2, -1)
    return rotation_matrices


def parse_relion30(raw_data, **kwargs):
    """Attempt to parse raw data dict from starfile.read as a RELION 3.0 style star file
    """
    if len(raw_data.values()) > 1:
        raise ParseError("Cannot parse as RELION 3.0 format STAR file")

    df = list(raw_data.values())[0]
    return extract_data(df, mode='3.0', **kwargs)


def parse_relion31(raw_data, **kwargs):
    """Attempt to parse raw data from starfile.read as a RELION 3.1 style star file
    """
    if list(raw_data.keys()) != ['optics', 'particles']:
        raise ParseError("Cannot parse as RELION 3.1 format STAR file")

    df = raw_data['particles'].merge(raw_data['optics'])
    return extract_data(df, mode='3.1', **kwargs)


reader_functions = {
    'relion_3.0': parse_relion30,
    'relion_3.1': parse_relion31,
}
