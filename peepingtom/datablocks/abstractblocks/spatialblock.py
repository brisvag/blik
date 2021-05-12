from abc import ABC

import numpy as np


class SpatialBlock(ABC):
    """
    provides spatial-related methods and properties
    """
    def __init__(self, *, pixel_size=1, dims_order='xyz', ndim=3, **kwargs):
        self._pixel_size = pixel_size
        self._dims_order = dims_order
        self._ndim = ndim
        super().__init__(**kwargs)

    @property
    def pixel_size(self):
        # cannot put in setter, otherwise views and children will overwrite parent time
        value = self.parent._pixel_size
        if value is None or np.all(value == 0):
            value = np.ones(self.ndim)
        else:
            value = np.broadcast_to(value, self.ndim)
        return value

    @property
    def dims_order(self):
        return self.parent._dims_order

    @property
    def ndim(self):
        return self.parent._ndim

    @property
    def dims(self):
        """
        names and order of spatial dimensions
        """
        return tuple(self.parent._dims_order[-self.ndim:])
