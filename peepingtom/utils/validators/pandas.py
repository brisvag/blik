import pandas as pd


def columns_in_df(columns: list, df: pd.DataFrame):
    """
    Checks that a list of columns are all present in a given DataFrame
    Parameters
    ----------
    columns : list of column names to check
    df : DataFrame to be checked

    Returns bool
    -------

    """
    return all([col in df for col in columns])
