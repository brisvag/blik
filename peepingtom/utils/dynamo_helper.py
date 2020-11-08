import numpy as np
import pandas as pd
from eulerangles import euler2matrix

from .validators import columns_in_df
from .constants.dynamo_constants import dynamo_table_coordinate_headings, dynamo_table_shift_headings, \
    dynamo_euler_angle_headings


def df_to_xyz(df: pd.DataFrame):
    """

    Parameters
    ----------
    df : dynamo format table file as DataFrame (usually the result of dynamotable.read)

    Returns (n, 3) ndarray of xyz positions from the DataFrame
    -------

    """
    assert columns_in_df(dynamo_table_coordinate_headings + dynamo_table_shift_headings, df)
    xyz = df[dynamo_table_coordinate_headings] + df[dynamo_table_shift_headings]
    return xyz.to_numpy()


def df_to_euler_angles(df: pd.DataFrame):
    """

    Parameters
    ----------
    df : dynamo format table file as DataFrame (usually the result of dynamotable.read)

    Returns (n, 3) ndarray of euler angles (tdrot, tilt, narot) from dataframe
    -------

    """
    assert columns_in_df(dynamo_euler_angle_headings)
    euler_angles = df[dynamo_euler_angle_headings]
    return euler_angles.to_numpy()


def euler_angles_to_rotation_matrices(euler_angles: np.ndarray):
    """

    Parameters
    ----------
    euler_angles : (n, 3) ndarray of euler angles (tdrot, tilt, narot) from dataframe

    Returns (n, 3, 3) ndarray of rotation matrices which premultiple column vectors [x, y, z]
    -------

    """
    return euler2matrix(euler_angles, axes='ZXZ', extrinsic=True, positive_ccw=True)


def df_to_rotation_matrices(df: pd.DataFrame):
    """

    Parameters
    ----------
    df : dynamo format table file as DataFrame (usually the result of dynamotable.read)

    Returns (n, 3) ndarray of euler angles (tdrot, tilt, narot) from dataframe
    -------

    """
    euler_angles = df_to_euler_angles(df)
    rotation_matrices = euler_angles_to_rotation_matrices(euler_angles)
    return rotation_matrices
