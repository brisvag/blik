from .datalist import DataList
from .datacrate import DataCrate


class DataSet(DataList):
    """
    A container for a collection of DataCrates
    """
    _valid_type = DataCrate

    @property
    def crates(self):
        return self._data

    @property
    def blocks(self):
        return [block for crate in self.crates for block in crate]
