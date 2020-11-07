# Basic data structures
import numpy as np


class Child:
    """
    base class for all objects with a reference to a parent object from which the Child was derived
    """

    def __init__(self, parent=None, **kwargs):
        self.parent = parent


class ArrayContainer(np.ndarray, Child):
    """
    base class for extending the functionality of simple ndarray objects
    examples include adding commonly used functions as methods and coersion of shape
    """

    def __new__(cls, a, target_shape: tuple = None, **kwargs):
        obj = np.asarray(a, **kwargs).view(cls)
        if target_shape is not None:
            obj = obj.reshape(target_shape)
        return obj

    def __init__(self, a, **kwargs):
        super().__init__(**kwargs)

    def asarray(self):
        return np.asarray(self)

    def _index_as_self(self, index):
        return self[index]






class SmartList():
    """
    typed list that can be indexed n-dimensionally, also with properties of the elements
    """

    def __init__(self, basetype, iterable=()):
        super().__init__(iterable)
