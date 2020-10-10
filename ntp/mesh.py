from dataclasses import dataclass
from functools import cached_property
import numpy as np


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

    def _stack(self, *args):
        """
        stack attributes of Mesh object along new axis at axis 0
        :param args: passed to getattr()
        :return: stacked arrays
        """
        arrays = (getattr(self, arg) for arg in args)
        stacked_arrays = np.stack(arrays, axis=1)
        return stacked_arrays

    def _distance(self, *args):
        """
        calculate distance between two points 'A', 'B' or 'C' in triangles
        :param args: passed to getattr()
        :return: distances
        """
        return np.linalg.norm(self._stack(*args), axis=(1,2))

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

    def ACsq(self):
        return self.AC ** 2

    def BCsq(self):
        return self.BC ** 2

    @cached_property
    def surface_area(self):
        dot = np.dot(self.AB, self.AC)
        return 0.5 * np.sqrt((self.ABsq * self.ACsq) - (dot ** 2))
