import numpy as np

from .orientedpointblock import OrientedPointBlock
from ..simpleblocks import PropertyBlock
from ...depictors import ParticleDepictor, PropertyPlotDepictor, ClassPlotDepictor
from ...utils import listify


class ParticleBlock(OrientedPointBlock):
    """
    Represents a set of particles with coordinates, orientations and arbitrary properties
    """
    _depiction_modes = {
        'default': ParticleDepictor,
        'property_plot': PropertyPlotDepictor,
        'class_plot': ClassPlotDepictor,
    }

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

    @property
    def n(self):
        return self.positions.n

    def if_properties(self, conditions, index=False):
        """
        return a subset of the particles that satisfy the property conditions
        conditions: a list of property names and conditions, in string form, or a single string:
            ['prop1 > 3', 'prop2 <= 1']
            - elements will be joined with logical & and fed to df.query
        index: return indexes of values, not values themselves
        """
        # TODO: programmatic way to do it without strings?
        conditions = listify(conditions)
        query = ' & '.join(conditions)
        idx = np.array(self.properties.data.query(query).index)
        if index:
            return self[idx], idx
        else:
            return self[idx]

    def __shape_repr__(self):
        return f'{self.positions.data.shape}'
