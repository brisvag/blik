"""
Basic data structures and base
"""

from enum import Enum


class ImageType(Enum):

    tomogram = 0
    classification = 1


class SmartList():
    """
    typed list that can be indexed n-dimensionally, also with properties of the elements
    """
    def __init__(self, basetype, iterable=()):
        super().__init__(iterable)
