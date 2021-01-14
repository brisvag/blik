from ..datablocks import ParticleBlock, ImageBlock
from ..utils import DispatchList, listify


class DataList(DispatchList):
    """
    base class for DataCrates and DataSets that implements common functionality
    subclasses should define a valid type for the contents and a depictor type
    """
    _valid_type = None
    _depictor_type = None
    _ignore_dispatch = ('name', 'parent', 'depictor')

    def __init__(self, data, name=None, depictor=None, **kwargs):
        if isinstance(data, type(self)):
            data = data._data
        super().__init__(data, **kwargs)
        self._name = name
        if depictor is None:
            depictor = self._depictor_type(self)
        self.depictor = depictor

    def __new__(cls, data, **kwargs):
        # if a new instance is created, it has a parent and it contains the wrong types,
        # we should simply return a DispatchList of it, because the user is trying to get
        # a view of non-standard contents of the container
        try:
            cls._checktypes(data)
        except TypeError:
            if kwargs.get('parent') is None:
                # this happens if the instance was actually created incorrectly
                raise
            # else:
                # return DispatchList(data)
        return super().__new__(cls)

    @property
    def name(self):
        return self._name or f'#{hash(self)}'

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def blocks(self):
        return self.flatten()

    @property
    def particles(self, flatten=False):
        return self._if_types(ParticleBlock, flatten=flatten)

    @property
    def images(self, flatten=False):
        return self._if_types(ImageBlock, flatten=flatten)

    def _if_element(self, callable):
        def select(obj, condition):
            out = obj.__newchild__([])
            for el in obj:
                if isinstance(el, DataList):
                    sub = el._if_element(condition)
                    if sub:
                        out.append(sub)
                else:
                    if callable(el):
                        out.append(el)
            return out
        return select(self, callable)

    def _if_types(self, block_types, flatten=False):
        """
        return a view containing only the chosen block types
        """
        block_types = tuple(listify(block_types))
        def right_type(item):
            return isinstance(item, block_types)
        filtered = self._if_element(right_type)
        if flatten:
            return filtered.flatten()
        else:
            return filtered

    def __getitem__(self, key):
        if isinstance(key, str):
            for item in self:
                if item.name == key:
                    return item
            for item in self.flatten():
                if item.name == key:
                    return item
            raise KeyError(f'could not find an item called "{key}"')
        else:
            return super().__getitem__(key)

    @classmethod
    def _checktypes(cls, items):
        if isinstance(items, cls):
            items = items._data
        for item in listify(items):
            if not isinstance(item, cls._valid_type):
                raise TypeError(f'{cls.__name__} can only hold '
                                f'{cls._valid_type.__name__} objects, not {type(item).__name__}')

    def __name_repr__(self):
        if self.name is None:
            return ''
        else:
            return f'<{self.name}>'

    def __base_repr__(self):
        return f'{type(self).__name__}{self.__name_repr__()}({len(self)})'

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
        self._checktypes(other)
        return super().__add__(other)

    def __iadd__(self, other):
        self._checktypes(other)
        return super().__iadd__(other)

    def append(self, item):
        self._checktypes(item)
        super().append(item)

    def insert(self, i, item):
        self._checktypes(item)
        super().insert(i, item)

    def extend(self, other):
        self._checktypes(other)
        return super().extend(other)
