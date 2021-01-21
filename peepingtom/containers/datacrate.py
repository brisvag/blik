from .datalist import DataList
from ..datablocks import DataBlock
from ..depictors import DataCrateDepictor


class DataCrate(DataList):
    """
    A container for DataBlock objects which exist within the same n-dimensional reference space
    """
    _valid_type = DataBlock
    _depictor_type = DataCrateDepictor

    @property
    def dataset(self):
        return self._container

    def __and__(self, other):
        if isinstance(other, DataBlock):
            other = [other]
        return self + other

    def __iand__(self, other):
        if isinstance(other, DataBlock):
            other = [other]
        self += other
        return self

    def __rand__(self, other):
        if isinstance(other, DataBlock):
            return self + other
