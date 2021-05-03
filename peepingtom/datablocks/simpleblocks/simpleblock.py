import logging

from xarray import DataArray

from ..datablock import DataBlock


logger = logging.getLogger(__name__)


class SimpleBlock(DataBlock):
    """
    Base class for all simple DataBlock objects, data types which can be visualised by Depictors
    and are defined by a single xarray `data` attribute

    SimpleBlock objects must implement a data setter method as _data_setter which returns
    the appropriately formatted data

    Calling __getitem__ on a SimpleBlock will call __getitem__ on its data property and return a view
    """
    def __init__(self, data=(), **kwargs):
        super().__init__(**kwargs)
        self.data = data

    @property
    def data(self):
        if callable(self._data):
            logger.debug(f'loading data for lazy datablock "{self}"')
            self.data = self._data()
        return self._data

    @data.setter
    def data(self, data):
        if isinstance(data, type(self)):
            self._data = data.data
        elif isinstance(data, DataArray) or callable(data):
            self._data = data
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
        return self.__view__(self.data[key])

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        yield from self.data

    def __reversed__(self):
        yield from reversed(self.data)
