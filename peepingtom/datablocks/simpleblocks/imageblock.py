import logging

import numpy as np
from xarray import DataArray

from .simpleblock import SimpleBlock
from ...depictors import ImageDepictor


logger = logging.getLogger(__name__)


class ImageBlock(SimpleBlock):
    """
    n-dimensional image block
    data can be interpreted as n-dimensional images
    """
    _depiction_modes = {'default': ImageDepictor}

    def __init__(self, data=(), pixel_size=None, shape=None, ndim=None, **kwargs):
        # TODO this is a workaround until napari #2347 is fixed
        self.pixel_size = pixel_size  # no checking here, or we screw up lazy loading
        self._shape = shape
        self._ndim = ndim
        super().__init__(data, **kwargs)

    def _data_setter(self, data):
        data = np.asarray(data)  # asarray does not copy unless needed
        if data.ndim < 2:
            raise ValueError('images must have at least 2 dimensions')
        dims = ('z', 'y', 'x')
        data = DataArray(data, dims=dims[-data.ndim:])

        # set pixel_size if needed
        if self.pixel_size is None or np.all(self.pixel_size == 0):
            pixel_size = np.ones(data.ndim)
            pixel_size = np.broadcast_to(pixel_size, data.ndim)
            self.pixel_size = pixel_size

        return data

    @property
    def ndim(self):
        if callable(self._data):
            return self._ndim
        return self.data.ndim

    @property
    def dims(self):
        if callable(self._data):
            return len(self._shape)
        return self.data.dims

    @property
    def shape(self):
        if callable(self._data):
            return self._shape
        return self.data.shape

    def __shape_repr__(self):
        return f'{self.shape}'
