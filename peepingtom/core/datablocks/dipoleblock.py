import numpy as np

from .base import GroupBlock
from .pointblock import PointBlock
from peepingtom.utils.helpers.linalg_helper import align_vectors


class DipoleBlock(GroupBlock):
    """
    A DipoleBlock represents a set of n dipoles in an m-dimensional space
    defined by center points and end points
    """

    def __init__(self, centers: PointBlock, endpoints: PointBlock):
        # Set dipole info
        self.centers = PointBlock(centers)
        self.endpoints = PointBlock(endpoints)

        # Check endpoint shape matches that of centers centers
        self._check_shapes()

        # Set blocks for GroupBlock
        children = [centers, endpoints]
        super().__init__(children)

    def _data_setter(self, data):
        self._data = data

    @property
    def orientation_vectors(self):
        """
        Vectors describing shifts to apply on centers to arrive at endpoints
        """
        return self.endpoints.data - self.centers.data

    @property
    def normalised_orientation_vectors(self):
        """
        self.orientation_vectors normalised to length 1
        """
        # Calculate length of each vector, add trailing dimension
        norm = np.expand_dims(np.linalg.norm(self.orientation_vectors, axis=1), axis=-1)
        # Calculate and return normalised vectors
        return self.orientation_vectors / norm

    def _check_shapes(self):
        if self.centers.data.shape != self.endpoints.data.shape:
            raise ValueError('Shapes of centers and endpoints do not match')
        else:
            return True

    def rotation_matrices(self, vector: np.ndarray):
        """
        Parameters
        -------
        vector : np.ndarray
                 A vector which you would like to align with the orientation vectors of each dipole

        Returns
        -------
        rotation_matrices : (n, 3, 3) set of rotation matrices
                            Rotation matrices premultiply 'vector' to align it with the
                            orientation vectors of each dipole in this object
        """
        # only implemented for 3d rotations
        if self.centers.data.shape[1] != 3:
            raise NotImplementedError

        # force ndarray
        vector = np.asarray(vector).reshape(-1)

        # normalise vector
        normalised_vector = vector / np.linalg.norm(vector)

        # calculate rotation matrices
        rotation_matrices = align_vectors(normalised_vector, self.normalised_orientation_vectors)
        return rotation_matrices

