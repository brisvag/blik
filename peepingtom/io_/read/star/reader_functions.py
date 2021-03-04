"""This module contains various reader functions for parsing data from different types of STAR
files.

Each function should attempt to raise a ParseError quickly if it's not the right function
for reading a given file.

raw data is the dictionary produced by starfile.read()
"""
import numpy as np
import pandas as pd
import eulerangles

from ...utils import guess_name, ParseError
from ....datablocks import ParticleBlock


coord_headings = {
    '3d': [f'rlnCoordinate{axis}' for axis in 'XYZ'],
    '2d': [f'rlnCoordinate{axis}' for axis in 'XY']
}
euler_headings = {
    '3d': [f'rlnAngle{angle}' for angle in ('Rot', 'Tilt', 'Psi')],
    '2d': 'rlnAnglePsi'
}
shift_headings = {
    '3d': {
        '3.0': [f'rlnOrigin{axis}' for axis in 'XYZ'],
        '3.1': [f'rlnOrigin{axis}Angst' for axis in 'XYZ']
    },
    '2d': {
        '3.0': [f'rlnOrigin{axis}' for axis in 'XY'],
        '3.1': [f'rlnOrigin{axis}Angst' for axis in 'XYZ']
    }
}

pixel_size_headings = {
    '3.0': ['rlnPixelSize'],
    '3.1': ['rlnImagePixelSize']
}
micrograph_name_heading = 'rlnMicrographName'


def extract_data(df, mode='3.1', name_regex=None):
    particleblocks = []
    for micrograph_name, df_volume in df.groupby('rlnMicrographName'):
        if coord_headings['3d'][-1] in df.columns:
            dim = '3d'
        else:
            dim = '2d'

        name = guess_name(micrograph_name, name_regex)

        coords = df_volume[coord_headings[dim]].to_numpy(dtype=float)
        shifts = df_volume.get(shift_headings[dim][mode], pd.Series([0.0])).to_numpy()
        px_size = df_volume.get(pixel_size_headings[mode], pd.Series([1.0])).to_numpy()
        shifts = shifts / px_size
        coords += shifts

        eulers = df_volume.get(euler_headings[dim], pd.Series([0])).to_numpy()
        if dim == '3d':
            rotation_matrices = euler2matrix_rln(eulers)
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


def euler2matrix_rln(euler_angles):
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


def rotangle2matrix(angle):
    rad = np.deg2rad(np.array(angle).reshape(-1))
    matrices = np.zeros((rad.shape[0], 2, 2), dtype=float)
    cos = np.cos(rad)
    sin = np.sin(rad)
    matrices[:, 0, 0] = cos
    matrices[:, 0, 1] = -sin
    matrices[:, 1, 1] = cos
    matrices[:, 1, 0] = sin
    return matrices.swapaxes(-2, -1)


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
