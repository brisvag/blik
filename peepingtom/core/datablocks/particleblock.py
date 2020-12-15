from .orientedpointblock import OrientedPointBlock
from .propertyblock import PropertyBlock


class ParticleBlock(OrientedPointBlock):
    def __init__(self, positions, orientations, properties=None, metadata=None, **kwargs):
        # Initialise OrientedPointBlock
        super().__init__(positions, orientations, **kwargs)

        # Add PropertyBlock
        if properties is None:
            properties = {}
        self.properties = PropertyBlock(properties)
        if metadata is None:
            metadata = {}
        self.metadata = {}

    def __shape_repr__(self):
        return f'{self.positions.data.shape}'
