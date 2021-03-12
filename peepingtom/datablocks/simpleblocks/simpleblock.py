from dask import delayed
from xarray import DataArray

from ..datablock import DataBlock


class SimpleBlock(DataBlock):
    """
    Base class for all simple DataBlock objects, data types which can be visualised by Depictors
    and are defined by a single xarray `data` attribute

    SimpleBlock objects must implement a data setter method as _data_setter which returns
    the appropriately formatted data

    Calling __getitem__ on a SimpleBlock will call __getitem__ on its data property and return a view
    """

    def __init__(self, data=(), reader_function=None, **kwargs):
        super().__init__(**kwargs)
        self.reader_function = reader_function
        self.data = data

    @property
    def data(self):
        if callable(self._data):
            return self._data.compute()
        return self._data

    @data.setter
    def data(self, data):
        if isinstance(data, type(self)):
            self._data = data.data
        elif isinstance(data, DataArray):
            self._data = data
        elif callable(self._reader_function):
            self._data = self._reader_function(data)
        else:
            self._data = self._data_setter(data)
        self.update()

    def _data_setter(self, data):
        """
        takes raw data and returns it properly formatted to the SimpleBlock subclass specification.
        """
        raise NotImplementedError('SimpleBlocks must implement this method')

    @property
    def reader_function(self):
        return self._reader_function

    @reader_function.setter
    def reader_function(self, function):
        if function is None:
            self._reader_function = function
        else:
            self._reader_function = delayed(function)

    def __setitem__(self, key, value):
        self.data[key] = value
        self.update()

    def __getitem__(self, key):
        return self.__view__(self.data[key])

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        yield from self.data

    def __reversed__(self):
        yield from reversed(self.data)
