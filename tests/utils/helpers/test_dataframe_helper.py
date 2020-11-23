import pandas as pd
import numpy as np

from peepingtom.utils.helpers import dataframe_helper


df = pd.DataFrame({
    'rlnCoordinateX': [0, 1],
    'rlnCoordinateY': [0, 1],
    'rlnCoordinateZ': [0, 1],
    'rlnOriginX': [0, 1],
    'rlnOriginY': [0, 1],
    'rlnOriginZ': [0, 1],
    'rlnAngleRot': [0, 1],
    'rlnAngleTilt': [0, 1],
    'rlnAnglePsi': [0, 1],
    'rlnMicrographName': ['test0', 'test1']
})


def test_df_to_xyz():
    data = dataframe_helper.df_to_xyz(df, 'relion')
    assert isinstance(data, np.ndarray)
    assert data.shape == (2, 3)


def test_df_to_rotation_matrices():
    euler_angles = dataframe_helper.df_to_euler_angles(df, 'relion')
    assert isinstance(euler_angles, np.ndarray)
    assert euler_angles.shape == (2, 3)
    rotation_matrices = dataframe_helper.euler_angles_to_rotation_matrices(euler_angles, 'relion')
    assert isinstance(rotation_matrices, np.ndarray)
    assert rotation_matrices.shape == (2, 3, 3)
    rotation_matrices = dataframe_helper.df_to_rotation_matrices(df, 'relion')
    assert isinstance(rotation_matrices, np.ndarray)
    assert rotation_matrices.shape == (2, 3, 3)


def test_df_split_on_volume():
    groups = dataframe_helper.df_split_on_volume(df)
    assert len(groups.keys()) == 2
    assert 'test0' in groups
    assert 'test1' in groups
    assert isinstance(groups['test0'], pd.DataFrame)
    assert isinstance(groups['test1'], pd.DataFrame)
