import numpy as np
import pandas as pd
from eulerangles import euler2matrix

from peepingtom.utils.validators import columns_in_df
from peepingtom.utils.constants.relion_constants import relion_coordinate_headings_3d, relion_shift_headings_3d, \
    relion_euler_angle_headings

from .exceptions import RelionDataFrameError

def df_to_xyz(df: pd.DataFrame):
    """

    Parameters
    ----------
    df : RELION format STAR file as DataFrame (usually the result of starfile.read)

    Returns (n, 3) ndarray of xyz positions from the DataFrame
    -------

    """
    # get xyz coordinates from dataframe
    if not columns_in_df(relion_coordinate_headings_3d, df):
        raise RelionDataFrameError("Could not get coordinates from DataFrame")

    positions = df[relion_coordinate_headings_3d]

    # add shifts if present in dataframe
    if columns_in_df(relion_shift_headings_3d, df):
        positions += df[relion_shift_headings_3d]

    return positions.to_numpy()


def df_to_euler_angles(df: pd.DataFrame):
    """

    Parameters
    ----------
    df : RELION format STAR file as DataFrame (usually the result of starfile.read)

    Returns : (n, 3) ndarray of euler angles rot, tilt, phi from the DataFrame
    -------

    """
    if not columns_in_df(relion_euler_angle_headings, df):
        raise RelionDataFrameError("Could not get euler angles from DataFrame")
    euler_angles = df[relion_euler_angle_headings]
    return euler_angles.to_numpy()


def euler_angles_to_rotation_matrices(euler_angles: np.ndarray):
    """

    Parameters
    ----------
    euler_angles : (n, 3) ndarray or RELION euler angles

    Returns (n, 3, 3) ndarray of rotation matrices which premultiply column vectors [x, y, z]
    -------

    """
    return euler2matrix(euler_angles, axes='zyz', intrinsic=True, positive_ccw=True)


def df_to_rotation_matrices(df: pd.DataFrame):
    """

    Parameters
    ----------
    df : RELION format STAR file as DataFrame (usually the result of starfile.read)

    Returns : (n, 3, 3) ndarray of rotation matrices which premultiply column vectors [x, y, z]
    -------

    """
    euler_angles = df_to_euler_angles(df)
    rotation_matrices = euler_angles_to_rotation_matrices(euler_angles)
    return rotation_matrices


def df_split_on_volume(df: pd.DataFrame):
    """

    Parameters
    ----------
    df : RELION format STAR file as DataFrame (usually the result of starfile.read)

    Returns dict {name : df} of DataFrame objects
            one for each volume in a star file based on the 'rlnMicrographName' column
    -------

    """
    grouped = df.groupby('rlnMicrographName')
    return {name: _df for name, _df in grouped}
