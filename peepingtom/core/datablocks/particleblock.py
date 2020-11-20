import pandas as pd

from .base import GroupBlock
from .orientationblock import OrientationBlock
from .pointblock import PointBlock
from .propertyblock import PropertyBlock
from ...utils.helpers import dataframe_helper


class ParticleBlock(MultiBlock):
    def __init__(self, positions: PointBlock, orientations: OrientationBlock, properties: PropertyBlock, **kwargs):
        self.positions = PointBlock(positions)
        self.orientations = OrientationBlock(orientations)
        self.properties = PropertyBlock(properties)
        super().__init__(blocks=[self.positions, self.orientations, self.properties], **kwargs)

    @classmethod
    def from_dataframe(cls, df: pd.DataFrame, mode: str, **kwargs):
        """
        Create a ParticleBlock instance from a DataFrame in a known mode

        This method expects the DataFrame to already represent the desired subset of particles in the case where data
        contains particles from multiple volumes

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

        positions = PointBlock(dataframe_helper.df_to_xyz(df, mode))
        orientations = OrientationBlock(dataframe_helper.df_to_rotation_matrices(df, mode))
        properties = PropertyBlock(dataframe_helper.df_to_dict_of_arrays(df[data_columns]))
        return cls(positions, orientations, properties, **kwargs)

    def __shape_repr__(self):
        return f'{self.positions.data.shape}'
