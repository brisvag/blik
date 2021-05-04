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

    def _data_setter(self, data=None):
        return pd.DataFrame(data)

    def items(self):
        # numpy array instead of pandas series, for compatibility
        for k, v in self.data.items():
            yield k, np.array(v)

    def __getitem__(self, key):
        # this allows indexing using slices and/or functionality like ParticleBlock.if_properties()
        if isinstance(key, (list)) and all(isinstance(i, (int, bool)) for i in key) or \
                isinstance(key, (np.ndarray, pd.Index)):
            data = self.data.iloc.__getitem__(key)
        else:
            data = self.data.__getitem__(key)
        return self.__view__(data=data)

    def __shape_repr__(self):
        return f'({len(self.data)}, {len(self.data.columns)})'
