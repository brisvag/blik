import numpy as np
from xarray import DataArray

from .simpleblock import SimpleBlock
from ...depictors import ImageDepictor


class ImageBlock(SimpleBlock):
    """
    n-dimensional image block
    data can be interpreted as n-dimensional images
    """
    _depiction_modes = {'default': ImageDepictor}

    def __init__(self, data=(), pixel_size=None, **kwargs):
        super().__init__(data, **kwargs)
        # TODO this is a workaround until napari #2347 is fixed
        if pixel_size is None:
            pixel_size = np.ones(self.ndim)
        self.pixel_size = pixel_size

    def _data_setter(self, data):
        data = np.array(data)
        if data.ndim < 2:
            raise ValueError('images must have at least 2 dimensions')
        dims = ('z', 'y', 'x')
        return DataArray(data, dims=dims[-data.ndim:])

    @property
    def ndim(self):
        return self.data.ndim

    @property
    def dims(self):
        return self.data.dims

    def __shape_repr__(self):
        return f'{self.data.shape}'
