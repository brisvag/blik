from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union

import numpy as np

from .geometry_primitives import CroppingGeometry, Mesh


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
        self.cropping_geometry = None

    @property
    def mesh(self):
        return self._mesh

    @mesh.setter
    def mesh(self, mesh: Mesh):
        assert isinstance(mesh, Mesh)
        self._mesh = mesh

    @property
    def cropping_geometry(self):
        return self._cropping_geometry


    @cropping_geometry.setter
    def cropping_geometry(self, cropping_geometry: CroppingGeometry):
        assert isinstance(cropping_geometry, CroppingGeometry)
        self._cropping_geometry = cropping_geometry


class Sphere(TomographyModel):
    def __init__(self, volume_file: Union[Path, str]):
        super().__init__(volume_file)
        self.center = None
        self.edge_point = None

    def _check_point(self, point: np.ndarray) -> np.ndarray:
        """
        coerces point into 3 element numpy array with shape (3,)
        """
        return np.asarray(point).reshape(3)

    @property
    def center(self):
        return self._center

    @center.setter
    def center(self, center: np.ndarray):
        self._center = self._check_point(center)

    @property
    def radius(self):
        return np.linalg.norm(self.edge_point - self.center)

    @property
    def edge_point(self):
        return self._edge_point

    @edge_point.setter
    def edge_point(self, point: np.ndarray):
        self._edge_point = self._check_point(point)

