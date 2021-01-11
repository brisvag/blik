from .dispatchlist import DispatchList
from .datalist import DataList
from .datacrate import DataCrate


class DataSet(DataList):
    """
    A container for a collection of DataCrates
    """
    _valid_type = DataCrate

    def __init__(self, data, name=None, viewer=None, **kwargs):
        super().__init__(data, name, **kwargs)
#        self.peeper = Peeper(viewer)
