import pandas as pd

from peepingtom.utils.validators.pandas import columns_in_df


df = pd.DataFrame({0: [0], 1: [1]})


def test_columns_in_df():
    assert columns_in_df([0, 1], df) is True
    assert columns_in_df([0, 3], df) is False
    assert columns_in_df([0, 0, 0], df) is True
    assert columns_in_df([5], df) is False
