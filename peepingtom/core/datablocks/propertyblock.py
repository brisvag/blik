import numpy as np
import pandas as pd
from .base import SimpleBlock


class PropertyBlock(SimpleBlock):
    """
    PropertyBlock is a simple dataframe wrapper with datablock api
    data: dataframe or dict whose values all have the same length
    """
    def _data_setter(self, data):
        return pd.DataFrame(data)

    def items(self):
        # numpy array instead of pandas series, for compatibility
        for k, v in self.data.items():
            yield k, np.array(v)

    def __getitem__(self, key):
        # this allows indexing using slices and/or functionality like ParticleBlock.if_properties()
        if isinstance(key, (list)) and all(isinstance(i, (int, bool)) for i in key) or \
                isinstance(key, (np.ndarray, pd.Index)):
            return self.data.iloc.__getitem__(key)
        else:
            return super().__getitem__(key)

    @staticmethod
    def _merge_data(datablocks):
        return pd.concat([db.data for db in datablocks], ignore_index=True)

    @staticmethod
    def _stack_data(datablocks):
        return pd.concat([db.data for db in datablocks], ignore_index=True)
