import numpy as np

from .orientedpointblock import OrientedPointBlock
from .propertyblock import PropertyBlock
from ...utils import listify


class ParticleBlock(OrientedPointBlock):
    """
    Represents a set of particles with coordinates, orientations and arbitrary properties
    """
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

    def if_properties(self, conditions):
        """
        return a subset of the particles that satisfy the property conditions
        conditions: a list of property names and conditions, in string form:
            ['prop1 > 3', 'prop2 <= 1']
            - elements will be joined with logical & and fed to df.query
        """
        conditions = listify(conditions)
        query = ' & '.join(conditions)
        idx = np.array(self.properties.data.query(query).index)
        return self[idx]

    def __shape_repr__(self):
        return f'{self.positions.data.shape}'
