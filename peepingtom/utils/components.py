# Basic data structures
import numpy as np

class Child:
    """
    base class for all objects with p a reference to a parent object from which the Child was derived
    """
    def __init__(self, parent=None):
        self.parent = parent


class ArrayContainer(np.ndarray):
    """
    base class for extending the functionality of simple ndarray objects
    examples include adding commonly used functions as methods and coersion of shape
    """
    def __new__(cls, a, shape: tuple = None, **kwargs):
        obj = np.asarray(a, **kwargs).view(cls)

        if shape is not None:
            return obj.reshape(shape)
        else:
            return obj

    def __array_finalize__(self, obj):
        if obj is None:
            return


class SmartList():
    """
    typed list that can be indexed n-dimensionally, also with properties of the elements
    """
    def __init__(self, basetype, iterable=()):
        super().__init__(iterable)






