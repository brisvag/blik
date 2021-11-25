from abc import abstractmethod
import logging

from .datablock import DataBlock


logger = logging.getLogger(__name__)


class SimpleBlock(DataBlock):
    """
    Base class for all simple DataBlock objects, data types which can be visualised by Depictors
    and are defined by a single `data` attribute

    SimpleBlock objects must implement a data setter method as _data_setter which returns
    the appropriately formatted data

    Calling __getitem__ on a SimpleBlock will call __getitem__ on its data property and return a view
    """
    def __init__(self, *, data=None, **kwargs):
        """
        data: a single object (typically a numpy or dask array) containing data for the datablock
        """
        super().__init__(**kwargs)
        self._data = None
        self.data = data

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        if isinstance(data, type(self)):
            self._data = data.data
        elif data is None:
            self._data = None
        else:
            self._data = self._data_setter(data)
        self.update()

    @property
    def nbytes(self):
        return self.data.nbytes

    @abstractmethod
    def _data_setter(self, data):
        """
        takes raw data and returns it properly formatted to the SimpleBlock subclass specification.
        """

    def __setitem__(self, key, value):
        self.data[key] = value
        self.update()

    def __getitem__(self, key):
        return self.__view__(data=self.data[key])

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        yield from self.data

    def __reversed__(self):
        yield from reversed(self.data)

    def __repr__(self):
        data_repr = f'\n{self.data.__repr__()}'
        return f'{self.__short_repr__()}{data_repr}'
