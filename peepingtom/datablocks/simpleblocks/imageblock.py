import numpy as np

from .simpleblock import SimpleBlock
from ...depictors import ImageDepictor


class ImageBlock(SimpleBlock):
    """
    n-dimensional image block
    data can be interpreted as n-dimensional images
    """
    _depiction_modes = {'default': ImageDepictor}

    def __init__(self, data, pixel_size=1, **kwargs):
        super().__init__(data, **kwargs)
        self.pixel_size = pixel_size

    def _data_setter(self, image: np.ndarray):
        return np.array(image)

    @property
    def pixel_size(self):
        return self._pixel_size

    @pixel_size.setter
    def pixel_size(self, value):
        self._pixel_size = float(value)

    def ndim(self):
        return self.data.ndim

    @staticmethod
    def _stack_data(datablocks):
        return np.stack([db.data for db in datablocks])

    def __shape_repr__(self):
        return f'{self.data.shape}'
