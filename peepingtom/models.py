from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union


import numpy as np
from scipy.spatial import cKDTree

from .geometric_primitives import CroppingGeometry, Mesh, Line


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
        if isinstance(mesh, Mesh):
            self._mesh = mesh
        else:
            self._mesh = None

    @property
    def cropping_geometry(self):
        return self._cropping_geometry


    @cropping_geometry.setter
    def cropping_geometry(self, cropping_geometry: CroppingGeometry):
        if isinstance(cropping_geometry, CroppingGeometry):
            self._cropping_geometry = cropping_geometry
        else:
            self._cropping_geometry = None

    def _check_point(self, point: np.ndarray) -> np.ndarray:
        """
        coerces point into 3 element numpy array with shape (3,)
        """
        if point is not None:
            return np.asarray(point).reshape(3)
        return None


class Sphere(TomographyModel):
    def __init__(self, volume_file: Union[Path, str]):
        super().__init__(volume_file)
        self.center = None
        self.edge_point = None

    def derive_cropping_geometry(self):
        # TODO
        pass

    def derive_mesh(self):
        # TODO
        pass

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


class FilamentModel(TomographyModel, ABC):
    def __init__(self, line: Line, volume_file: Union[Path, str]):
        super().__init__(volume_file)
        self.line = line
        self.radius = None
        self.edge_point = None

    @property
    def backbone(self) -> np.ndarray:
        return self.line.backbone

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        self._radius = value

    @property
    def edge_point(self):
        return self._edge_point

    @edge_point.setter
    def edge_point(self, value):
        self._edge_point = self._check_point(value)
        self._update_radius_from_edge_point()

    @property
    def backbone_kdtree(self) -> cKDTree:
        return cKDTree(self.backbone)

    def _update_radius_from_edge_point(self):
        if self._check_point(self.edge_point) is not None:
            self.radius, _ = self.backbone_kdtree.query(self.edge_point, k=1)
        return














