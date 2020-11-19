import numpy as np

from .base import DataBlock


class ImageBlock(DataBlock):
    """
    n-dimensional image block
    data can be interpreted as n-dimensional images
    """

    def __init__(self, data, pixel_size=1, **kwargs):
        super().__init__(**kwargs)
        self.data = data
        self.pixel_size = pixel_size

    def _data_setter(self, image: np.ndarray):
        return image

    @property
    def pixel_size(self):
        return self._pixel_size

    @pixel_size.setter
    def pixel_size(self, value):
        self._pixel_size = float(value)

    def ndim(self):
        return self.data.ndim

    def dump(self):
        kwargs = super().dump()
        kwargs.update({'data': self.data})
        return kwargs

    @staticmethod
    def _stack(db1, db2):
        return np.stack([db1.data, db2.data])

    def __repr__(self):
        return f'<{type(self).__name__}{self.data.shape}>'
