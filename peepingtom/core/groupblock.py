"""
GroupBlock objects are groups of DataBlock objects which are commonly viewed and manipulated together
"""
import pandas as pd
import numpy as np

from .datablock import DataBlock, PointBlock, OrientationBlock, PropertyBlock
from ..utils.helpers import dataframe_helper


class GroupBlock(DataBlock):
    """
    unites multiple DataBlocks to construct a complex data object
    """
    def __init__(self, children):
        self.children = children


class ParticleBlock(GroupBlock):
    def __init__(self, positions: PointBlock, orientations: OrientationBlock, properties: PropertyBlock, **kwargs):
        self.positions = positions
        self.orientations = orientations
        self.properties = properties
        super().__init__(children=[self.positions, self.orientations, self.properties], **kwargs)
        self.data = self.positions

    def _data_setter(self, positions):
        self._data = positions

    @property
    def positions(self):
        return self._positions

    @positions.setter
    def positions(self, positions):
        if not isinstance(positions, PointBlock):
            positions = PointBlock(positions)
        self._positions = positions

    @property
    def orientations(self):
        return self._orientations

    @orientations.setter
    def orientations(self, orientations):
        if not isinstance(orientations, OrientationBlock):
            raise TypeError(f"""Expected type 'OrientationBlock' but got '{type(orientations)}' instead.
Construct an OrientationBlock or instantiate your ParticleBlock using one of the 'from_*' factory methods of this class
""")
        self._orientations = orientations

    @property
    def properties(self):
        return self._properties

    @properties.setter
    def properties(self, properties):
        if not isinstance(properties, PropertyBlock):
            properties = PropertyBlock(properties)
        self._properties = properties

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
