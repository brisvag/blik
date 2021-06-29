import numpy as np
import pandas as pd

from ..abstractblocks import SimpleBlock
from ...depictors import PropertyPlotDepictor


class PropertyBlock(SimpleBlock):
    """
    PropertyBlock is a simple dataframe wrapper with datablock api
    data: dataframe or dict whose values all have the same length
    """
    _depiction_modes = {
        'default': PropertyPlotDepictor
    }

    def __init__(self, *, protected=None, **kwargs):
        super().__init__(**kwargs)
        self._protected = protected or []

    def _data_setter(self, data=None):
        try:
            data = pd.DataFrame(data)
        except ValueError:
            data = pd.DataFrame(np.array(data).reshape(-1))
        return data

    @property
    def n(self):
        return len(self)

    def items(self):
        # numpy array instead of pandas series, for compatibility
        for k, v in self.data.items():
            yield k, np.array(v)

    def __setitem__(self, key, value):
        # does not work on view (we lose track of how nested we are and how we got here)
        if self.is_view():
            raise TypeError('cannot set data with nested getitem calls.')
        # this allows indexing using slices and/or functionality like ParticleBlock.if_properties()
        if isinstance(key, (list)) and all(isinstance(i, (int, bool)) for i in key) or \
                isinstance(key, (np.ndarray, pd.Index)):
            self.data.iloc.__setitem__(key, value)
        else:
            if key in self._protected:
                raise KeyError(f'"{key}" is a protected property and cannot be changed')
            self.data.__setitem__(key, value)

    def __getitem__(self, key):
        # this allows indexing using slices and/or functionality like ParticleBlock.if_properties()
        if isinstance(key, (list)) and all(isinstance(i, (int, bool)) for i in key) or \
                isinstance(key, (np.ndarray, pd.Index)):
            data = self.data.iloc.__getitem__(key)
        else:
            data = self.data.__getitem__(key)
        return self.__view__(data=data)

    def __shape_repr__(self):
        return f'({self.data.shape})'
