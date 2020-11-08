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

