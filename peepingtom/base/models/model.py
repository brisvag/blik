from abc import ABC

from ..datablock import DataBlock


class Model(DataBlock, ABC):
    """
    A Model is a DataBlock from which a CroppingGeometry can be derived
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def derive_cropping_geometry(self):
        pass
