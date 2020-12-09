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

    def __shape_repr__(self):
        return f'{self.positions.data.shape}'
