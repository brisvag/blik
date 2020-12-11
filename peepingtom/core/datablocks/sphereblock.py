import numpy as np

from .base import SimpleBlock


class SphereBlock(SimpleBlock):
    def __init__(self, center: np.ndarray, radius: float = None, **kwargs):
        super().__init__(**kwargs)
        # TODO: check if below works
        self.data = center, radius
        self.edge_point = None

    def _data_setter(self, center: np.ndarray, radius: float = None):
        self.center = center
        self.radius = float(radius)
        return self.center, self.radius

    @property
    def center(self):
        return self._center

    @center.setter
    def center(self, point: np.ndarray):
        return np.asarray(point).reshape(3)

    @property
    def edge_point(self):
        return self._edge_point

    @edge_point.setter
    def edge_point(self, edge_point: np.ndarray):
        edge_point = np.asarray(edge_point).reshape(3)
        self._edge_point = edge_point
        self._update_radius_from_edge_point()

    def _update_radius_from_edge_point(self):
        self.radius = np.linalg.norm(self.center - self.edge_point)
