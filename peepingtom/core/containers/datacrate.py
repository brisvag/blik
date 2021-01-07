from ..datablocks import DataBlock
from ...utils import AttributedList


class DataCrate(AttributedList):
    """
    A container for DataBlock objects which exist within the same n-dimensional reference space
    """
    def __init__(self, iterable_or_datablock=()):
        # recursively unpack the iterable into datablocks only
        def unpack(iterable):
            datablocks = []
            if isinstance(iterable, (list, tuple)):
                for item in iterable:
                    datablocks.extend(unpack(item))
            else:
                datablocks.append(iterable)
            return datablocks

        items = unpack(iterable_or_datablock)
        self._checktypes(items)
        super().__init__(items)

    @staticmethod
    def _checktypes(items):
        for item in items:
            if not isinstance(item, DataBlock):
                raise TypeError(f'DataCrate can only hold DataBlocks, not {type(item)}')

    def __add__(self, other):
        if isinstance(other, list):
            self._checktypes(other)
            return DataCrate(super().__add__(other))
        if isinstance(other, DataBlock):
            return self + DataCrate([other])
        else:
            return NotImplemented

    def __iadd__(self, other):
        if isinstance(other, list):
            self._checktypes(other)
            super().__iadd__(other)
            return self
        if isinstance(other, DataBlock):
            super().__iadd__([other])
            return self
        else:
            return NotImplemented

    def __and__(self, other):
        if isinstance(other, (list, DataBlock)):
            return self + other
        else:
            return NotImplemented

    def __iand__(self, other):
        if isinstance(other, (list, DataBlock)):
            self += other
            return self
        else:
            return NotImplemented

    def __base_repr__(self):
        return f'{type(self).__name__}({len(self)})'

    def __repr__(self):
        return f'<{self.__base_repr__()}: [{", ".join([datablock.__base_repr__() for datablock in self])}]>'
