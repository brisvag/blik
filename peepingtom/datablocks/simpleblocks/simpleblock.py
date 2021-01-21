from ..datablock import DataBlock


class SimpleBlock(DataBlock):
    """
    Base class for all simple DataBlock objects, data types which can be visualised by Depictors

    SimpleBlock objects must implement a data setter method as _data_setter which returns
    the appropriately formatted data

    Calling __getitem__ on a SimpleBlock will call __getitem__ on its data property
    """
    def __init__(self, data, **kwargs):
        super().__init__(**kwargs)
        self.data = data

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        if isinstance(data, type(self)):
            self._data = data.data
        else:
            self._data = self._data_setter(data)
        self.update()

    def _data_setter(self, data):
        """
        takes raw data and returns it properly formatted to the SimpleBlock subclass specification.
        """
        raise NotImplementedError('SimpleBlocks must implement this method')

    def __setitem__(self, key, value):
        self.data[key] = value
        self.update()

    def __getitem__(self, key):
        return self.__newlike__(self.data[key])

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        yield from self.data

    def __reversed__(self):
        yield from reversed(self.data)

    def _merge(self, datablocks):
        merged = self._merge_data(datablocks)
        if merged is NotImplemented:
            return NotImplemented
        return self.__newlike__(merged)

    def _stack(self, datablocks):
        stacked = self._stack_data(datablocks)
        if stacked is NotImplemented:
            return NotImplemented
        return self.__newlike__(self._stack_data(datablocks))

    def _imerge(self, datablocks):
        merged = self._merge_data([self] + datablocks)
        if merged is NotImplemented:
            return NotImplemented
        self.data = merged

    def _istack(self, datablocks):
        stacked = self._stack_data([self] + datablocks)
        if stacked is NotImplemented:
            return NotImplemented
        self.data = stacked
