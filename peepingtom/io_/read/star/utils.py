from pathlib import Path

import eulerangles

from ....core import ParticleBlock


def rln30_df_to_particleblocks(df):
    """Generate a list of ParticleBlocks from a RELION 3.0 style star file
    """
    coord_headings = [f'rlnCoordinate{axis}' for axis in 'XYZ']
    shift_headings = [f'rlnOrigin{axis}' for axis in 'XYZ']
    euler_headings = [f'rlnAngle{angle}' for angle in ('Rot', 'Tilt', 'Psi')]

    particleblocks = []

    for micrograph_name, df_ in df.groupby('rlnMicrographName'):
        name = Path(micrograph_name).stem

        coords = df_[coord_headings]
        shifts = df_.get(shift_headings, 0)
        xyz = (coords + shifts).to_numpy()

        eulers = df_[euler_headings]
        rotation_matrices = euler2matrix_rln(eulers)

        properties = {key: df[key].to_numpy() for key in df.columns}

        particleblocks.append(ParticleBlock(xyz, rotation_matrices, properties, name=name))

    return particleblocks


def rln31_df_to_particleblocks(df):
    """Generate a list of ParticleBlocks from a RELION 3.1 style star file dataframe
    """
    coord_headings = [f'rlnCoordinate{axis}' for axis in 'XYZ']
    shift_headings = [f'rlnOrigin{axis}Angstrom' for axis in 'XYZ']
    pixel_size_heading = 'rlnImagePixelSize'
    euler_headings = [f'rlnAngle{angle}' for angle in ('Rot', 'Tilt', 'Psi')]

    particleblocks = []

    for micrograph_name, df_ in df.groupby('rlnMicrographName'):
        name = Path(micrograph_name).stem

        coords = df_[coord_headings]
        shifts_px = df_[shift_headings] / df[pixel_size_heading]
        xyz = (coords + shifts_px).to_numpy()

        eulers = df_[euler_headings]
        rotation_matrices = euler2matrix_rln(eulers)

        properties = {key: df[key].to_numpy() for key in df.columns}

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

