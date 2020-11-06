"""
Basic data structures and base
"""

from enum import Enum


class ImageType(Enum):
    image = 0
    multi_frame_micrograph = 1
    micrograph = 2
    tilt_series = 3
    tomogram = 4
    cross_correlation_volume = 5


class SmartList():
    """
    typed list that can be indexed n-dimensionally, also with properties of the elements
    """
    def __init__(self, basetype, iterable=()):
        super().__init__(iterable)
