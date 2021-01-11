from .dispatchlist import DispatchList
from .datalist import DataList
from .datacrate import DataCrate


class DataSet(DataList):
    """
    A container for a collection of DataCrates
    """
    _valid_type = DataCrate
