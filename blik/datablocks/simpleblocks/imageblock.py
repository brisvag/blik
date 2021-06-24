import logging

import numpy as np

from ..abstractblocks import SpatialBlock, SimpleBlock
from ...depictors import ImageDepictor


logger = logging.getLogger(__name__)


class ImageBlock(SpatialBlock, SimpleBlock):
    """
    Image block

    data must have at least 2 dims; spatial dimensions are ordered zyx
    """
    _depiction_modes = {'default': ImageDepictor}

    def _data_setter(self, data):
        data = np.asarray(data)  # asarray does not copy unless needed
        if data.ndim < 2:
            raise ValueError('images must have at least 2 dimensions')
        if data.ndim == 2:
            # prepend z dim if missing
            data = data[np.newaxis]
        return data

    @property
    def shape(self):
        return self.data.shape

    @property
    def is_3D(self):
        return self.shape[-3] > 1

    def __shape_repr__(self):
        return f'{self.shape}'
