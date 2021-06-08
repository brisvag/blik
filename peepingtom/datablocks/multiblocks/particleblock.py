import numpy as np

from .orientedpointblock import OrientedPointBlock
from ..simpleblocks import PropertyBlock
from ...depictors import ParticleDepictor
from ...utils import listify


class ParticleBlock(OrientedPointBlock):
    """
    Represents a set of particles with coordinates, orientations and arbitrary properties
    """
    _block_types = {'properties': PropertyBlock}
    _depiction_modes = {
        'default': ParticleDepictor,
    }

    def __init__(self, *, metadata=None, **kwargs):
        super().__init__(**kwargs)
        self.metadata = metadata or {}

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
