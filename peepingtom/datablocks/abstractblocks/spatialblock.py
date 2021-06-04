from abc import ABC

import numpy as np


class SpatialBlock(ABC):
    """
    provides spatial-related methods and properties
    """
    def __init__(self, *, pixel_size=1, dims_order='xyz', ndim=3, **kwargs):
        self._dims_order = dims_order
        self._ndim = ndim
        super().__init__(**kwargs)
        # this needs to be after super, because the previous ones are needed for init, but this would break
        # due to `parent` not existing yet and having a setter that needs it
        self.pixel_size = pixel_size

    @property
    def pixel_size(self):
        return self.parent._pixel_size

    @pixel_size.setter
    def pixel_size(self, value):
        # cast to float first, so np.any can work
        if isinstance(value, np.ndarray):
            value = value.astype(float)
        else:
            value = float(value)
        if not np.any(value):
            value = np.ones(self.ndim)
        else:
            value = np.broadcast_to(value, self.ndim)
        self.parent._pixel_size = value
        self.update()

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
        return tuple(self.parent._dims_order[:self.ndim])
