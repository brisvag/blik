from abc import ABC, abstractmethod

import numpy as np


class SpatialBlock(ABC):
    """
    provides spatial-related methods and properties
    """
    def __init__(self, *, pixel_size=1, **kwargs):
        super().__init__(**kwargs)
        # this needs to be after super, because the previous ones are needed for init, but this would break
        # due to `parent` not existing yet and having a setter that needs it
        self.pixel_size = pixel_size

    @property
    def pixel_size(self):
        pixel_size = self.parent._pixel_size
        # calculate on get, not on set, so we can set without triggering lazy loader
        # cast to float first, so np.any can work
        if isinstance(pixel_size, np.ndarray):
            pixel_size = pixel_size.astype(float)
        else:
            pixel_size = float(pixel_size)
        if not np.any(pixel_size):
            pixel_size = np.ones(self.ndim)
        else:
            pixel_size = np.broadcast_to(pixel_size, self.ndim)
        return pixel_size

    @pixel_size.setter
    def pixel_size(self, value):
        self.parent._pixel_size = value
        self.update()

    @abstractmethod
    def _ndim(self):
        pass

    @property
    def ndim(self):
        """
        return the number of spatial dimensions of this datablock
        """
        if hasattr(self, '._loaded') and not self._loaded:
            return 1
        # view_of instead of parent, lets us have different ndim for blocks inside multiblock, if ever useful
        return self.view_of._ndim()

