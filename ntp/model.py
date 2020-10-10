from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union

import numpy as np


class Model(ABC):
    def __init__(self, volume_file: Union[Path, str]):
        self.volume_file = Path(volume_file)

    @abstractmethod
    def derive_mesh(self):
        pass

    @abstractmethod
    def derive_cropping_geometry(self):
        pass


class TomographyModel(Model, ABC):
    def __init__(self, volume_file: Union[Path, str]):
        super().__init__(volume_file)
        self.mesh = None

    @property
    def mesh(self):
        return self._mesh

    @mesh.setter
    def mesh(self, mesh):
        self._mesh = mesh


