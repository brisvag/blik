from pathlib import Path

import pandas as pd
import eulerangles

from ....core import ParticleBlock


def rln30_df_to_particleblocks(df):
    """Generate a list of ParticleBlocks from a RELION 3.0 style star file
    """
    coord_headings = [f'rlnCoordinate{axis}' for axis in 'XYZ']
    shift_headings = [f'rlnOrigin{axis}' for axis in 'XYZ']
    euler_headings = [f'rlnAngle{angle}' for angle in ('Rot', 'Tilt', 'Psi')]

    particleblocks = []

    for micrograph_name, df_volume in df.groupby('rlnMicrographName'):
        name = Path(micrograph_name).stem

        coords = df_volume[coord_headings].to_numpy()
        shifts = df_volume.get(shift_headings, pd.Series([0])).to_numpy()
        xyz = coords + shifts

        eulers = df_volume[euler_headings]
        rotation_matrices = euler2matrix_rln(eulers)

        properties = {key: df_volume[key].to_numpy() for key in df.columns}

        particleblocks.append(ParticleBlock(xyz, rotation_matrices, properties, name=name))

    return particleblocks


def rln31_df_to_particleblocks(df):
    """Generate a list of ParticleBlocks from a RELION 3.1 style star file dataframe
    """
    coord_headings = [f'rlnCoordinate{axis}' for axis in 'XYZ']
    shift_headings = [f'rlnOrigin{axis}Angst' for axis in 'XYZ']
    pixel_size_heading = ['rlnImagePixelSize']
    euler_headings = [f'rlnAngle{angle}' for angle in ('Rot', 'Tilt', 'Psi')]

    particleblocks = []

    for micrograph_name, df_volume in df.groupby('rlnMicrographName'):
        name = Path(micrograph_name).stem

        coords = df_volume[coord_headings].to_numpy()
        shifts = df_volume[shift_headings].to_numpy()
        pixel_size = df_volume[pixel_size_heading].to_numpy()
        shifts_px = shifts / pixel_size
        xyz = coords + shifts_px

        eulers = df_volume[euler_headings]
        rotation_matrices = euler2matrix_rln(eulers)

        properties = {key: df_volume[key].to_numpy() for key in df_volume.columns}

        particleblocks.append(ParticleBlock(xyz, rotation_matrices, properties, name=name))

    return particleblocks


def euler2matrix_rln(euler_angles):
    """
    Convert (n, 3) array of RELION euler angles to rotation matrices
    Resulting rotation matrices rotate references into particles
    """
    rotation_matrices = eulerangles.euler2matrix(euler_angles,
                                                 axes='zyz',
                                                 intrinsic=True,
                                                 positive_ccw=True)

    rotation_matrices = rotation_matrices.swapaxes(-2, -1)
    return rotation_matrices

