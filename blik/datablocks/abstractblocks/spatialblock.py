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
        return self.parent._pixel_size

    @pixel_size.setter
    def pixel_size(self, pixel_size):
        # cast to float first, so np.any can work
        if isinstance(pixel_size, np.ndarray):
            pixel_size = pixel_size.astype(float)
        else:
            pixel_size = float(pixel_size)
        if not np.any(pixel_size):
            # sometimes values are set to 0 in files, and that's obviously wrong
            pixel_size = np.ones(3)
        else:
            pixel_size = np.broadcast_to(pixel_size, 3)
        self.parent._pixel_size = pixel_size
        self.update()

    @property
    @abstractmethod
    def is_3D(self):
        """
        return whether the datablock contains any information in the third dimension
        """
