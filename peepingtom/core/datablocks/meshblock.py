import numpy as np

from .pointblock import PointBlock


class MeshBlock(PointBlock):
    """
    Data structure for holding n-dimensional mesh data
    """
    def __init__(self, vertices: np.ndarray, faces: np.ndarray, **kwargs):
        """

        Parameters
        ----------
        vertices : array of shape (v, m)
                   v vertices in m dimensions
        faces : array of shape (f, 3)
                array of indices into the vertices defining connectivity
        kwargs : keyword arguments passed to SimpleBlock
        """
        super().__init__(data=vertices, **kwargs)
        self.vertices = vertices
        self.faces = faces
        self.data = self.vertices

    @property
    def vertices(self):
        return self._vertices

    @vertices.setter
    def vertices(self, vertices: np.ndarray):
        self._vertices = np.asarray(vertices)

    @property
    def faces(self):
        return self._faces

    @faces.setter
    def faces(self, faces: np.ndarray):
        faces = np.asarray(faces)
        if faces.shape[1] != 3:
            raise ValueError('shape of faces must be (f, 3)')
        self._faces = faces

    @property
    def triangles(self):
        triangles = self.vertices[self.faces]
        return triangles

    @property
    def midpoints(self):
        """
        Calculate the midpoints of each triangle in the mesh
        Returns
        -------
        midpoints : (n, m)
                    n midpoints in m dimensions
        """
        return self.triangles.mean(axis=1)
