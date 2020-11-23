from pathlib import Path

import pandas as pd
import numpy as np
import starfile

from peepingtom.utils.helpers import dataframe_helper


test_root = Path(__file__).parent.parent.parent
df = starfile.read(test_root / 'test_data/relion_3d_simple.star')


def test_df_to_xyz():
    data = dataframe_helper.df_to_xyz(df, 'relion')
    assert isinstance(data, np.ndarray)
    assert data.shape == (50, 3)


def test_df_to_rotation_matrices():
    euler_angles = dataframe_helper.df_to_euler_angles(df, 'relion')
    assert isinstance(euler_angles, np.ndarray)
    assert euler_angles.shape == (50, 3)
    rotation_matrices = dataframe_helper.euler_angles_to_rotation_matrices(euler_angles, 'relion')
    assert isinstance(rotation_matrices, np.ndarray)
    assert rotation_matrices.shape == (50, 3, 3)
    rotation_matrices = dataframe_helper.df_to_rotation_matrices(df, 'relion')
    assert isinstance(rotation_matrices, np.ndarray)
    assert rotation_matrices.shape == (50, 3, 3)


def test_df_split_on_volume():
    groups = dataframe_helper.df_split_on_volume(df)
    assert len(groups.keys()) == 1
    assert 'test_tomo' in groups
    assert isinstance(groups['test_tomo'], pd.DataFrame)
