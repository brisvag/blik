import numpy as np
import pandas as pd

from ..validators import columns_in_df
from ..constants import relion_coordinate_headings_3d, relion_shift_headings_3d, \
    relion_euler_angle_headings, dynamo_table_coordinate_headings, dynamo_table_shift_headings, \
    dynamo_euler_angle_headings
from .eulerangle_helper import EulerAngleHelper
from ..exceptions import DataFrameError


def _check_mode(mode):
    modes = ['relion', 'dynamo']
    if mode not in modes:
        raise ValueError(f'mode can only be one of {modes}; got {mode}')


def df_to_xyz(df: pd.DataFrame, mode: str):
    """

    Parameters
    ----------
    df : RELION format STAR file as DataFrame (usually the result of starfile.read)

    mode: one of 'relion', 'dynamo'

    Returns (n, 3) ndarray of xyz positions from the DataFrame
    -------

    """
    coord_columns = {
        'relion': relion_coordinate_headings_3d,
        'dynamo': dynamo_table_coordinate_headings
    }
    shift_columns = {
        'relion': relion_shift_headings_3d,
        'dynamo': dynamo_table_shift_headings,
    }
    _check_mode(mode)
    # get xyz coordinates from dataframe
    if not columns_in_df(coord_columns[mode], df):
        raise DataFrameError("Could not get coordinates from DataFrame")

    positions = df[coord_columns[mode]].to_numpy()
    if columns_in_df(df, shift_columns[mode]):
        positions += df[shift_columns[mode]].to_numpy()

    return positions


def df_to_euler_angles(df: pd.DataFrame, mode: str):
    """

    Parameters
    ----------
    df : RELION format STAR file as DataFrame (usually the result of starfile.read)

    Returns : (n, 3) ndarray of euler angles rot, tilt, phi from the DataFrame
    -------

    """
    angle_columns = {
        'relion': relion_euler_angle_headings,
        'dynamo': dynamo_euler_angle_headings,
    }
    _check_mode(mode)
    if not columns_in_df(angle_columns[mode], df):
        print(angle_columns[mode], df.columns)
        raise DataFrameError("Could not get euler angles from DataFrame")
    euler_angles = df[angle_columns[mode]]
    return euler_angles.to_numpy()


def euler_angles_to_rotation_matrices(euler_angles: np.ndarray, mode: str):
    """

    Parameters
    ----------
    euler_angles : (n, 3) array of float
                   of Euler angles in a mode EulerAngleHelper can handle

    Returns
    rotation_matrices : (n, 3, 3) array of float
                        rotation matrices which premultiply column vectors [x, y, z] to align them with the
                        reference frame of a particle
    -------

    """
    rotation_matrices = EulerAngleHelper(euler_angles=euler_angles).euler2matrix(mode)
    return rotation_matrices


def df_to_rotation_matrices(df: pd.DataFrame, mode: str):
    """

    Parameters
    ----------
    df : RELION format STAR file as DataFrame (usually the result of starfile.read)

    Returns
    -------
    rotation_matrices: (n, 3, 3) ndarray of float
                       rotation matrices which premultiply column vectors [x, y, z]
    """
    euler_angles = df_to_euler_angles(df, mode)
    rotation_matrices = euler_angles_to_rotation_matrices(euler_angles, mode)
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


def df_to_dict_of_arrays(df):
    """
    transform a dataframe into dictionary of numpy arrays
    """
    return {key: df[key].to_numpy() for key in df}
