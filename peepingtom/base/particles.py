from eulerangles import euler2matrix
import pandas as pd

from .datablock import PointBlock, OrientationBlock
from ..utils.components import Child
import peepingtom.utils.relion_helper as relion_helper
import peepingtom.utils.dynamo_helper as dynamo_helper


class Particles(Child):
    def __init__(self, positions: PointBlock, orientations: OrientationBlock, **kwargs):
        super().__init__(**kwargs)
        self.positions = positions
        self.orientations = orientations

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

    @staticmethod
    def _from_relion_star_dataframe(df: pd.DataFrame):
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
        positions = PointBlock(relion_helper.df_to_xyz(df))
        orientations = OrientationBlock(relion_helper.df_to_rotation_matrices(df))
        return Particles(positions, orientations, parent=df)

    @staticmethod
    def _from_dynamo_table_dataframe(df: pd.DataFrame):
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
        positions = PointBlock(dynamo_helper.df_to_xyz(df))
        orientations = OrientationBlock(dynamo_helper.df_to_rotation_matrices(df))
        return Particles(positions, orientations, parent=df)
