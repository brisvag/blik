from .dispatchlist import DispatchList


class DataList(DispatchList):
    """
    base class for DataCrates and DataSets that implements common functionality
    """
    _valid_type = None
    _ignore_dispatch = ('name', 'parent')

    def __init__(self, data, name=None, **kwargs):
        super().__init__(data, **kwargs)
        if self._parent is None:
            # only check if no parent exists (messes with dispatch list functionality)
            self._checktypes(self)
        self._name = name

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @classmethod
    def _checktypes(cls, items):
        for item in items:
            if not isinstance(item, cls._valid_type):
                raise TypeError(f'{cls.__name__} can only hold '
                                f'{cls._valid_type.__name__} objects, not {type(item).__name__}')

    def __base_repr__(self):
        return f'{type(self).__name__}<{self.name}>({len(self)})'

    def __pprint__(self, indent=0):
        """
        called to recursively create a pretty print representation
        """
        indent += 1
        indent_multiplier = 4
        try:
            display_contents = [f'{el.__pprint__(indent)}' for el in self]
        except AttributeError:
            display_contents = [f'{el}' for el in self]
        if len(display_contents) > 7:
            display_contents = display_contents[:3] + ['...'] + display_contents[-3:]
        total_indent = indent * indent_multiplier
        display_contents = f',\n{" " * total_indent}'.join(display_contents)
        return f'{self.__base_repr__()}:\n{" " * (total_indent - 1)}[{display_contents}]'

    def __repr__(self):
        return self.__pprint__()

    def __add__(self, other):
        if isinstance(other, type(self)):
            self._checktypes(other)
            return self.__newlike__(self._data + other._data)
        if isinstance(other, list):
            return self + self.__newlike__(other)
        else:
            return NotImplemented

    def __iadd__(self, other):
        if isinstance(other, type(self)):
            self._checktypes(other)
            self._data += other._data
            return self
        if isinstance(other, list):
            self += self.__newlike__(other)
            return self
        else:
            return NotImplemented
