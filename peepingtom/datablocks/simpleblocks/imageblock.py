import logging

import numpy as np
from xarray import DataArray

from ..abstractblocks import SpatialBlock, SimpleBlock
from ...depictors import ImageDepictor


logger = logging.getLogger(__name__)


class ImageBlock(SpatialBlock, SimpleBlock):
    """
    Image block
    """
    _depiction_modes = {'default': ImageDepictor}

    def _data_setter(self, data):
        data = np.asarray(data)  # asarray does not copy unless needed
        if data.ndim < 2:
            raise ValueError('images must have at least 2 dimensions')
        elif data.ndim > 3:
            raise NotImplementedError('images with more than 3 dimensions are not yet implemented')
        data = DataArray(data, dims=self.dims)
        if data.dims != self.dims:
            raise ValueError(f'data {dict(data.sizes)} does not match '
                             f'expected shape {self.dims}')
        return data

    @property
    def shape(self):
        return self.data.shape
