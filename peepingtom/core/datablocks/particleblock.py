import numpy as np

from .orientedpointblock import OrientedPointBlock
from .propertyblock import PropertyBlock


class ParticleBlock(OrientedPointBlock):
    def __init__(self, positions: np.ndarray, orientations: np.ndarray, properties: dict, **kwargs):
        # Initialise OrientedPointBlock
        super().__init__(positions, orientations, **kwargs)

        # Add PropertyBlock
        self.properties = PropertyBlock(properties)

    def __shape_repr__(self):
        return f'{self.positions.data.shape}'
