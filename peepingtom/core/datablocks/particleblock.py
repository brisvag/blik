import numpy as np
import pandas as pd

from .orientedpointblock import OrientedPointBlock
from .propertyblock import PropertyBlock
from ...utils.helpers import dataframe_helper


class ParticleBlock(OrientedPointBlock):
    def __init__(self, positions: np.ndarray, orientations: np.ndarray, properties: dict, **kwargs):
        # Initialise OrientedPointBlock
        super().__init__(positions, orientations, **kwargs)

        # Add PropertyBlock
        self.properties = PropertyBlock(properties)

    @classmethod
    def from_dataframe(cls, df: pd.DataFrame, mode: str, **kwargs):
        """
        Create a ParticleBlock instance from a DataFrame in a known mode

        This method expects the DataFrame to already represent the desired subset of particles
        in the case where data contains particles from multiple volumes

        Parameters
        ----------
        df: pandas DataFrame for particles from one volume of a RELION format star file DataFrame
            df should already represent the desired, single volume subset of particles

        mode: str, 'relion' or 'dynamo'
        Returns
        -------

        """
        data_columns = []
        if 'data_columns' in kwargs:
            data_columns = kwargs.pop('data_columns')

        positions = dataframe_helper.df_to_xyz(df, mode)
        orientations = dataframe_helper.df_to_rotation_matrices(df, mode)
        properties = dataframe_helper.df_to_dict_of_arrays(df[data_columns])
        return cls(positions, orientations, properties, **kwargs)

    def __shape_repr__(self):
        return f'{self.positions.data.shape}'
