from .datalist import DataList
from ..datablocks import DataBlock


class DataCrate(DataList):
    """
    A container for DataBlock objects which exist within the same n-dimensional reference space
    """
    _valid_type = DataBlock

    @property
    def blocks(self):
        return self._data
