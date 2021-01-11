import numpy as np
import pandas as pd
from ...utils import listify


class DispatchList:
    """
    list-like class that can dispatch getitem, getattr, setattr and calls to its contents,
    while retaining its original structure intact.

    special methods and attributes such as `loc`, methods that starting with a `_`, or provided
    in the _ignore_dispatch class attribute in subclasses will get around this.

    By default, getitem acts on the list itself. To dispatch, use it on the `.loc` attribute
    """
    _ignore_dispatch = ()

    def __init__(self, iterable=(), parent=None):
        self._data = listify(iterable)
        if parent is None:
            parent = self
        self._parent = parent
        self.loc = ItemDispatcher(self)

    def __newlike__(self, *args, parent=None, **kwargs):
        return type(self)(*args, parent=parent, **kwargs)

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

    def _dispatchable(self, name):
        """
        returns whether or not to dispatch the attribute call
        """
        if name.startswith('_') or name in self._ignore_dispatch or name in ('loc'):
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
            [el.__setattr__(name, value) for el in self._data]

    def __call__(self, *args, **kwargs):
        return self.__newchild__([el(*args, **kwargs) for el in self._data])

    def __iter__(self):
        yield from self._data

    def __contains__(self, item):
        found = item in self._data
        if not found:
            for el in self:
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
        self._data.__delitem__(key)

    def __setitem__(self, key, value):
        self._data.__setitem__(key, value)

    def __repr__(self):
        return self._data.__repr__()

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
        else:
            self._data.extend(other)


class ItemDispatcher:
    def __init__(self, parent):
        self.parent = parent

    def __getitem__(self, key):
        items = []
        for el in self.parent:
            if isinstance(el, DispatchList):
                items.extend(el.loc[key])
            else:
                items.append(el[key])
        return self.parent.__newchild__(items)

    def __setitem__(self, key, value):
        for el in self.parent:
            if isinstance(el, DispatchList):
                el.loc[key] = value
            else:
                el[key] = value
