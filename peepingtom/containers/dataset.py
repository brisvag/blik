from .datalist import DataList
from .datacrate import DataCrate
from ..depictors import DataSetDepictor


class DataSet(DataList):
    """
    A container for a collection of DataCrates
    """
    _valid_type = DataCrate
    _depictor_type = DataSetDepictor
