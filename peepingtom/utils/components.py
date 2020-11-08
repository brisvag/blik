"""
Basic data structures
"""

import numpy as np


class Child:
    """
    base class for all objects with a reference to a parent object from which the Child was derived
    """

    def __init__(self, parent=None, **kwargs):
        self.parent = parent

    @property
    def parent_properties(self):
        return getattr(self.parent, 'properties', None)



class SmartList():
    """
    typed list that can be indexed n-dimensionally, also with properties of the elements
    """

    def __init__(self, basetype, iterable=()):
        super().__init__(iterable)
