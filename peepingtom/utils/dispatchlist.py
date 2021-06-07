class DispatchList:
    """
    list-like class that can dispatch getitem, getattr, setattr and calls to its contents,
    while retaining its original structure intact.

    methods that starting with a `_` and attributes provided in the _ignore_dispatch class attribute
    will get around this. Subclasses can define a new list of _ignore_dispatch: the parent classes values
    will still be checked against.

    By default, getitem acts on the list itself. To force dispatch to the most nested level,
    use it on the `.disp` attribute
    """
    _ignore_dispatch = ('disp',)

    def __init__(self, iterable=(), parent=None):
        # avoid circular import
        from .generic import listify
        self._data = listify(iterable)
        if parent is None:
            parent = self
        self._parent = parent
        self.disp = ItemDispatcher(self)

    def __newlike__(self, *args, **kwargs):
        return type(self)(*args, **kwargs)

    def __newchild__(self, *args, **kwargs):
        return self.__newlike__(*args, parent=self._parent, **kwargs)

    def __getattribute__(self, name):
        try:
            return super().__getattribute__(name)
        except AttributeError:
            try:
                return self.__getattr__(name)
            except AttributeError:
                raise AttributeError(f"{type(self).__name__} and its contents have no attribute '{name}'")

    @classmethod
    def _dispatchable(cls, name):
        """
        returns whether or not to dispatch the attribute call
        """
        if name.startswith('_'):
            return False
        else:
            ignore = []
            for parent in cls.mro():
                ignore.extend(getattr(parent, '_ignore_dispatch', ()))
            if name in ignore:
                return False
        return True

    def __getattr__(self, name):
        # ignore under and (d)under methods
        if not self._dispatchable(name):
            raise AttributeError(f"{type(self).__name__} has no attribute '{name}'")
        return self.__newchild__([el.__getattribute__(name) for el in self._data])

    def __setattr__(self, name, value):
        # ignore under and (d)under methods
        if not self._dispatchable(name):
            return super().__setattr__(name, value)

        try:
            present = self.__getattribute__(name)
        except AttributeError:
            present = None

        if not isinstance(present, type(self)):
            # the attribute was found at the top level, or the attribute wasn't found
            # either way, set it to the top level (parent)
            self._parent.__dict__[name] = value
        else:
            # dispatch to lower levels
            [el.__setattr__(name, value) for el in self]

    def __call__(self, *args, **kwargs):
        return self.__newchild__([el(*args, **kwargs) for el in self])

    def __iter__(self):
        yield from self._data

    def __contains__(self, item):
        found = item in self._data
        if not found:
            for el in self._data:
                try:
                    found = item in el
                except TypeError:
                    found = False
        return found

    def __len__(self):
        return len(self._data)

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._data[key]
        else:
            return self.__newchild__(self._data[key])

    def __delitem__(self, key):
        del self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value

    def __add__(self, other):
        if isinstance(other, DispatchList):
            return self.__newlike__(self._data + other._data)
        elif isinstance(other, list):
            return self.__newlike__(self._data + other)
        else:
            return NotImplemented

    def __iadd__(self, other):
        if isinstance(other, DispatchList):
            self._data += other._data
            return self
        elif isinstance(other, list):
            self._data += other
            return self
        else:
            return NotImplemented

    def __eq__(self, other):
        if isinstance(other, DispatchList):
            return self._data == other._data
        elif isinstance(other, list):
            return self._data == other
        else:
            return all(item == other for item in self)

    def __repr__(self):
        return f'*{self._data.__repr__()}*'

    def append(self, item):
        self._data.append(item)

    def insert(self, i, item):
        self._data.insert(i, item)

    def pop(self, i=-1):
        return self._data.pop(i)

    def reverse(self):
        self._data.reverse()

    def extend(self, other):
        if isinstance(other, DispatchList):
            self._data.extend(other._data)
        elif isinstance(other, list):
            self._data.extend(other)
        else:
            return NotImplemented

    def index(self, item, *args):
        return self._data.index(item, *args)

    def flatten(self):
        out = DispatchList()
        for el in self:
            if isinstance(el, DispatchList):
                out.extend(el.flatten())
            else:
                out.append(el)
        return out


class ItemDispatcher:
    def __init__(self, parent):
        self.parent = parent

    def __getitem__(self, key):
        items = []
        for el in self.parent:
            if isinstance(el, DispatchList):
                items.extend(el.disp[key])
            else:
                items.append(el[key])
        return self.parent.__newchild__(items)

    def __setitem__(self, key, value):
        for el in self.parent:
            if isinstance(el, DispatchList):
                el.disp[key] = value
            else:
                el[key] = value
