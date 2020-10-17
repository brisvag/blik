from dataclasses import dataclass
from functools import cached_property
from pathlib import Path

import numpy as np
from scipy.interpolate import splprep, splev

from ntp.linalg import normalise


class Line:
    def __init__(self, points: np.ndarray = np.zeros(3)):
        self.points = points
        self.smoothing_parameter = 0.5

    @property
    def points(self):
        return self._points

    @points.setter
    def points(self, points: np.ndarray):
        self._points = np.asarray(points).reshape(-1, 3)

    def _get_point_idx(self, idx):
        """
        get points at index along axis 1
        """
        return self.points[:, idx]

    @property
    def x(self):
        return self._get_point_idx(0)

    @property
    def y(self):
        return self._get_point_idx(1)

    @property
    def z(self):
        return self._get_point_idx(2)

    @property
    def n_points(self):
        return self.points.shape[0]

    @property
    def smoothing_parameter(self):
        return self._smoothing_parameter

    @smoothing_parameter.setter
    def smoothing_parameter(self, s: float):
        self._smoothing_parameter = float(s)

    @property
    def spline(self) -> tuple:
        return splprep([self.x, self.y, self.z], s=self.smoothing_parameter)

    def _calculate_smooth_backbone(self, n_samples):
        self.spline_tck, self.spline_u = self.spline
        self.u_fine = np.linspace(self.spline_u.min(), self.spline_u.max(), n_samples, endpoint=True)
        smooth_backbone = np.column_stack(splev(self.u_fine, self.spline_tck))
        return smooth_backbone

    @property
    def backbone(self):
        return self._calculate_smooth_backbone(1000)

    @property
    def backbone_vectors(self):
        backbone_plus_delta = np.column_stack(splev(self.u_fine + 1e-3, self.spline_tck))
        delta = backbone_plus_delta - self.backbone
        return normalise(delta)


@dataclass
class CroppingGeometry:
    """
    parent : volume file associated with this cropping geometry
    crop_points : positions at which particles should be cropped
    rotation_matrices : (N,3,3) rotation matrices describing rotation of unit vectors to arrive at orientation of particle
    """
    parent: Path
    crop_points: np.ndarray
    rotation_matrices: np.ndarray


@dataclass
class Mesh:
    """
    vertices - (V, 3) array containing XYZ positions where V is the number of vertices
    faces - (F, 3) array containing indices for the vertices which make up the face
    """
    vertices: np.ndarray
    faces: np.ndarray

    @cached_property
    def triangles(self):
        return self.vertices[self.faces]

    def points(self, idx):
        """
        get points in triangles by index
        :param idx: idx of point
        :return:
        """
        return self.triangles[:, idx, :].reshape((-1, 3))

    @cached_property
    def A(self):
        return self.points(0)

    @cached_property
    def B(self):
        return self.points(1)

    @cached_property
    def C(self):
        return self.points(2)

    def _distance(self, x, y):
        """
        calculate distance between two points (x and y) from 'A', 'B' or 'C' in triangles
        :param args: passed to getattr()
        :return: distances
        """
        x = getattr(self, x)
        y = getattr(self, y)
        return np.linalg.norm(x - y, axis=1)

    @cached_property
    def AB(self):
        return self._distance('A', 'B')

    @cached_property
    def AC(self):
        return self._distance('A', 'C')

    @cached_property
    def BC(self):
        return self._distance('B', 'C')

    @cached_property
    def ABsq(self):
        return self.AB ** 2

    @cached_property
    def ACsq(self):
        return self.AC ** 2

    @cached_property
    def BCsq(self):
        return self.BC ** 2

    # @cached_property
    # def surface_area(self):
    #     dot = np.dot(self.AB, self.AC)
    #     sqrt = np.sqrt((self.ABsq * self.ACsq) - (dot ** 2))
    #     return 0.5 * sqrt