from .datalist import DataList
from ..datablocks import DataBlock
from ..depictors import DataCrateDepictor


class DataCrate(DataList):
    """
    A container for DataBlock objects which exist within the same n-dimensional reference space
    """
    _valid_type = DataBlock
    _depictor_type = DataCrateDepictor
