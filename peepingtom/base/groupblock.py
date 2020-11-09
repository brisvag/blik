import pandas as pd

from .datablock import DataBlock, PointBlock, OrientationBlock
from ..utils.helpers import dataframe_helper


class GroupBlock(DataBlock):
    """
    unites multiple DataBlocks to construct a complex data object
    """


class Particles(GroupBlock):
    def __init__(self, positions: PointBlock, orientations: OrientationBlock, properties: pd.DataFrame, **kwargs):
        super().__init__(**kwargs)
        self.positions = positions
        self.orientations = orientations
        self.properties = properties
        self.data = self.positions

    def _data_setter(self, value):
        self._data = value

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
        if not isinstance(OrientationBlock):
            raise TypeError(f"""Expected type 'OrientationBlock' but got '{type(orientations)}' instead.
Construct an OrientationBlock or instantiate your Particles using one of the 'from_*' factory methods of this class
""")
        self._orientations = orientations

    @classmethod
    def _from_star_dataframe(cls, df: pd.DataFrame, mode: str):
        """
        Create a Particles instance from a RELION format star file DataFrame

        This method expects the DataFrame to already represent the desired subset of particles in the case where data
        contains particles from multiple volumes

        Parameters
        ----------
        df: pandas DataFrame for particles from one volume of a RELION format star file DataFrame
            df should already represent the desired, single volume subset of particles

        Returns
        -------

        """
        positions = PointBlock(dataframe_helper.df_to_xyz(df, mode))
        orientations = OrientationBlock(dataframe_helper.df_to_rotation_matrices(df, mode))
        return cls(positions, orientations)
