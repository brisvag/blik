import numpy as np
import pandas as pd
from .base import SimpleBlock


class PropertyBlock(SimpleBlock):
    """
    PropertyBlock is a simple dataframe wrapper with datablock api
    """
    def _data_setter(self, data):
        return pd.DataFrame(data)

    def items(self):
        # numpy array instead of pandas series, for compatibility
        for k, v in self.data.items():
            yield k, np.array(v)

    @staticmethod
    def _merge_data(datablocks):
        return pd.concat([db.data for db in datablocks], ignore_index=True)

    @staticmethod
    def _stack_data(datablocks):
        return pd.concat([db.data for db in datablocks], ignore_index=True)
