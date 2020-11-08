from pandas import DataFrame
from eulerangles import euler2matrix

from .validators import columns_in_df
from .constants.relion_constants import relion_coordinate_headings_3d, relion_shift_headings_3d, relion_euler_angle_headings


def df_to_xyz(df: DataFrame):
    """

    Parameters
    ----------
    df : RELION format STAR file as DataFrame (usually the result of starfile.read)

    Returns (n, 3) ndarray of xyz positions from the DataFrame
    -------

    """
    # get xyz coordinates from dataframe
    assert columns_in_df(relion_coordinate_headings_3d, df)
    positions = df[relion_coordinate_headings_3d]

    # add shifts if present in dataframe
    if columns_in_df(relion_shift_headings_3d, df):
        positions += df[relion_shift_headings_3d]

    return positions.to_numpy()


def df_to_euler_angles(df: DataFrame):
    """

    Parameters
    ----------
    df : RELION format STAR file as DataFrame (usually the result of starfile.read)

    Returns : (n, 3) ndarray of euler angles rot, tilt, phi from the DataFrame
    -------

    """
    assert columns_in_df(relion_euler_angle_headings, df)
    euler_angles = df[relion_euler_angle_headings]
    return euler_angles.to_numpy()


def df_to_rotation_matrices(df: DataFrame):
    """

    Parameters
    ----------
    df : RELION format STAR file as DataFrame (usually the result of starfile.read)

    Returns : (n, 3, 3) ndarray of rotation matrices which premultiply column vectors [x, y, z]
    -------

    """
    euler_angles = df_to_euler_angles(df)
    rotation_matrices = euler2matrix(euler_angles, axes='zyz', intrinsic=True, positive_ccw=True)
    return rotation_matrices