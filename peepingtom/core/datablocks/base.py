from abc import ABC, abstractmethod


class DataBlock(ABC):
    """
    Base class for all simple DataBlock objects, data types which can be visualised by Depictors

    DataBlock objects must implement a data setter method as _data_setter which returns the appropriately formatted data

    Calling __getitem__ on a DataBlock will call __getitem__ on its data property
    """
    def __init__(self, parent=None):
        self.parent = parent

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, *args):
        self._data = self._data_setter(*args)
        self.updated()

    @abstractmethod
    def _data_setter(self, data):
        self.data = data

    def dump(self):
        kwargs = {}
        kwargs.update({'parent': self.parent})
        return kwargs

    def updated(self):
        """
        this function is called when getitem is used.
        It is used by other modules to know when the data was changed.
        When needed, it can be patched with additional callbacks.
        """

    def __newlike__(self, *args, **kwargs):
        cls = type(self)
        return cls(parent=self.parent, *args, **kwargs)

    def __getitem__(self, key):
        return self.data.__getitem__(key)

    def __setitem__(self, key, value):
        self.data.__setitem__(key, value)
        # signal that data was updated
        self.updated()

    def __delitem__(self, key):
        self.data.__delitem__(key)
        # signal that data was updated
        self.updated()

    def __contains__(self, item):
        return self.data.__contains__(item)

    def __len__(self):
        return self.data.__len__()

    def __iter__(self):
        return self.data.__iter__()

    def __reversed__(self):
        return self.data.__reversed__()

    def __repr__(self):
        return f'<{type(self).__name__}>'

    def __and__(self, other):
        if isinstance(other, DataBlock):
            return DataCrate([self, other])
        elif isinstance(other, DataCrate):
            return DataCrate([self]) + other
        else:
            return NotImplemented

    def __iand__(self, other):
        return NotImplemented

    @staticmethod
    def _merge(db1, db2):
        """
        merge two datablocks of the same type into one, within the same ndimensional space
        """
        return NotImplemented

    @staticmethod
    def _stack(db1, db2):
        """
        stack two Datablock objects into one. If dimensionality is the same,
        add a new dimension; otherwise, use the next available dimension for the
        datablock with smaller dimensionality
        """
        return NotImplemented

    def __add__(self, other):
        if isinstance(other, type(self)):
            return self.__newlike__(self._merge(self, other))
        else:
            return NotImplemented

    def __iadd__(self, other):
        if isinstance(other, type(self)):
            self.data = self._merge(self, other)
            return self
        else:
            return NotImplemented

    def __or__(self, other):
        if isinstance(other, type(self)):
            return self.__newlike__(self._stack(self, other))
        else:
            return NotImplemented

    def __ior__(self, other):
        if isinstance(other, type(self)):
            self.data = self._stack(self, other)
            return self
        else:
            return NotImplemented


class GroupBlock(DataBlock, ABC):
    """
    unites multiple DataBlocks to construct a complex data object
    """
    def __init__(self, children, parent=None):
        """

        Parameters
        ----------
        children :
        parent
        """
        super().__init__(parent=parent)
        self.children = children

    def __newlike__(self, *args, **kwargs):
        cls = type(self)
        return cls(parent=self.parent, *args, **kwargs)

    @staticmethod
    def _merge(db1, db2):
        blocks = []
        for block1, block2 in zip(db1.children, db2.children):
            blocks.append(block1 + block2)
        return blocks

    @staticmethod
    def _stack(db1, db2):
        blocks = []
        for block1, block2 in zip(db1.children, db2.children):
            blocks.append(block1 | block2)
        return blocks

    @staticmethod
    def _imerge(db1, db2):
        for block1, block2 in zip(db1.children, db2.children):
            block1 += block2

    @staticmethod
    def _istack(db1, db2):
        for block1, block2 in zip(db1.children, db2.children):
            block1 |= block2

    def __add__(self, other):
        if isinstance(other, type(self)):
            return self.__newlike__(*self._merge(self, other))
        else:
            return NotImplemented

    def __iadd__(self, other):
        if isinstance(other, type(self)):
            self._imerge(self, other)
            return self
        else:
            return NotImplemented

    def __or__(self, other):
        if isinstance(other, type(self)):
            return self.__newlike__(*self._stack(self, other))
        else:
            return NotImplemented

    def __ior__(self, other):
        if isinstance(other, type(self)):
            self._istack(self, other)
            return self
        else:
            return NotImplemented



class DataCrate(list):
    """
    A container for DataBlock objects which exist within the same n-dimensional reference space
    """
    def __and__(self, other):
        if isinstance(other, DataCrate):
            return DataCrate(self + other)
        elif isinstance(other, DataBlock):
            return DataCrate(self + [other])
        else:
            return NotImplemented

    def __iand__(self, other):
        if isinstance(other, DataCrate):
            self += other
            return self
        elif isinstance(other, DataBlock):
            self += DataCrate([other])
            return self
        else:
            return NotImplemented

    def __repr__(self):
        return f'<DataCrate{[datablock for datablock in self]}>'
