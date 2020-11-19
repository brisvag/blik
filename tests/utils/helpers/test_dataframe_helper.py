import pandas as pd
import numpy as np
import starfile

from peepingtom.utils.helpers import dataframe_helper


df = starfile.read('../../test_data/relion_3d_simple.star')


def test_df_to_xyz():
    data = dataframe_helper.df_to_xyz(df, 'relion')
    assert isinstance(data, np.ndarray)
    assert data.shape == (50, 3)
