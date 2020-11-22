from abc import ABC, abstractmethod

from ...utils.containers import AttributedList


class BaseBlock(ABC):
    """
    Base class for all simple and complex datablocks.
    Provides common methods and easy type inference
    """
    def __init__(self, parent=None, depictor=None):
        self.parent = parent
        self.depictor = depictor

    def dump(self):
        kwargs = {}
        kwargs.update({'parent': self.parent, 'depictor': self.depictor})
        return kwargs

    def updated(self):
        """
        this function is called when the data changed in order to trigger callbacks
        """
        if self.depictor is not None:
            self.depictor.update()

    def __newlike__(self, *args, **kwargs):
        # this makes sure that operators get the right output in case
        # _merge or _stack return notimplemented
        if args[0] is NotImplemented:
            return NotImplemented
        cls = type(self)
        return cls(parent=self.parent, *args, **kwargs)

    def __shape_repr__(self):
        return ''

    def __base_repr__(self):
        return f'{type(self).__name__}{self.__shape_repr__()}'

    def __repr__(self):
        return f'<{self.__base_repr__()}>'

    def __and__(self, other):
        if isinstance(other, BaseBlock):
            return DataCrate([self, other])
        elif isinstance(other, DataCrate):
            return DataCrate([self]) + other
        else:
            return NotImplemented

    def __iand__(self, other):
        return NotImplemented

    @staticmethod
    def _merge_data(datablocks):
        """
        convenience method to merge the data of several datablocks
        of the same type into one, within the same ndimensional space
        used by merge and imerge.
        """
        return NotImplemented

    @staticmethod
    def _stack_data(datablocks):
        """
        convenience method to stack the data of several datablocks into one.
        If dimensionality is the same, add a new dimension; otherwise,
        use the next available dimension for the datablocks with smaller dimensionality
        used by stack and istack.
        """
        return NotImplemented

    def _merge(self, datablocks):
        """
        merge several datablocks and return a `newlike` object
        self is not part of merged objects
        """
        return NotImplemented

    def _stack(self, datablocks):
        """
        stack several datablocks and return a `newlike` object
        self is not part of stacked objects
        """
        return NotImplemented

    def _imerge(self, datablocks):
        """
        like merge, but inplace. Self is part of merged objects.
        """
        return NotImplemented

    def _istack(self, datablocks):
        """
        like stack, but inplace. Self is part of stacked objects.
        """
        return NotImplemented

    def __add__(self, other):
        if isinstance(other, type(self)):
            return self._merge([self, other])
        else:
            return NotImplemented

    def __iadd__(self, other):
        if isinstance(other, type(self)):
            self._imerge([other])
            return self
        else:
            return NotImplemented

    def __or__(self, other):
        if isinstance(other, type(self)):
            return self._stack([self, other])
        else:
            return NotImplemented

    def __ior__(self, other):
        if isinstance(other, type(self)):
            self._istack([other])
            return self
        else:
            return NotImplemented


class DataBlock(BaseBlock, ABC):
    """
    Base class for all simple DataBlock objects, data types which can be visualised by Depictors

    DataBlock objects must implement a data setter method as _data_setter which returns the appropriately formatted data

    Calling __getitem__ on a DataBlock will call __getitem__ on its data property
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
        self.updated()

    @abstractmethod
    def _data_setter(self, data):
        return data

    def dump(self):
        kwargs = super().dump()
        kwargs.update({'data': self.data})
        return kwargs

    def __getitem__(self, key):
        return self.data.__getitem__(key)

    def __setitem__(self, key, value):
        self.data.__setitem__(key, value)
        self.updated()

    def __delitem__(self, key):
        self.data.__delitem__(key)
        self.updated()

    def __contains__(self, item):
        return self.data.__contains__(item)

    def __len__(self):
        return self.data.__len__()

    def __iter__(self):
        return self.data.__iter__()

    def __reversed__(self):
        return self.data.__reversed__()

    def _merge(self, datablocks):
        return self.__newlike__(self._merge_data(datablocks))

    def _stack(self, datablocks):
        return self.__newlike__(self._stack_data(datablocks))

    def _imerge(self, datablocks):
        self.data = self._merge_data([self] + datablocks)

    def _istack(self, datablocks):
        self.data = self._stack_data([self] + datablocks)


class MultiBlock(BaseBlock, ABC):
    """
    unites multiple DataBlocks to construct a more complex data object
    constructor requires a list of references to the component DataBlocks
    in order to know where to find them
    """
    def __init__(self, blocks, **kwargs):
        super().__init__(**kwargs)
        self.blocks = blocks

    @staticmethod
    def _merge_data(multiblocks):
        blocks_data = []
        blocks_all = [mb.blocks for mb in multiblocks]
        # cryptic loop example: datablock types in "blocks" (a, b, c),
        # this loops through the list [(a1, a2, ...), (b1, b2, ...), (c1, c2, ...)]
        # so this separates the components of a list of multiblocks into a lists of
        # simple datablocks of the same type
        for blocks_by_type in zip(*blocks_all):
            blocks_data.append(blocks_by_type[0]._merge_data(blocks_by_type))
        return blocks_data

    @staticmethod
    def _stack_data(multiblocks):
        blocks_data = []
        blocks_all = [mb.blocks for mb in multiblocks]
        # cryptic loop example: datablock types in "blocks" (a, b, c),
        # this loops through the list [(a1, a2, ...), (b1, b2, ...), (c1, c2, ...)]
        # so this separates the components of a list of multiblocks into a lists of
        # simple datablocks of the same type
        for blocks_by_type in zip(*blocks_all):
            blocks_data.append(blocks_by_type[0]._stack_data(blocks_by_type))
        return blocks_data

    def _merge(self, multiblocks):
        return self.__newlike__(*self._merge_data(multiblocks))

    def _stack(self, multiblocks):
        return self.__newlike__(*self._stack_data(multiblocks))

    def _imerge(self, multiblocks):
        new_data = self._merge_data([self] + multiblocks)
        for block, data in zip(self.blocks, new_data):
            block.data = data

    def _istack(self, multiblocks):
        new_data = self._stack_data([self] + multiblocks)
        for block, data in zip(self.blocks, new_data):
            block.data = data


class DataCrate(AttributedList):
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

    def __base_repr__(self):
        return f'{type(self).__name__}({len(self)})'

    def __repr__(self):
        return f'<{self.__base_repr__()}: [{", ".join([datablock.__base_repr__() for datablock in self])}]>'
