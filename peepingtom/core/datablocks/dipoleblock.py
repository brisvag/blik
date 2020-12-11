import numpy as np

from .base import MultiBlock
from .pointblock import PointBlock
from .orientationblock import OrientationBlock
from ...utils import align_vectors


class DipoleBlock(MultiBlock):
    """
    A DipoleBlock represents a set of n dipoles in an m-dimensional space
    defined by start points and end points
    """

    def __init__(self, startpoints: np.ndarray, endpoints: np.ndarray, **kwargs):
        super().__init__(**kwargs)
        # Set dipole info
        self.startpoints = PointBlock(startpoints)
        self.endpoints = PointBlock(endpoints)

        # Check endpoint shape matches that of startpoints
        self._check_shapes()

    @property
    def orientation_vectors(self):
        """
        Vectors describing shifts to apply on start points to arrive at end points
        """
        return self.endpoints.data - self.startpoints.data

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
        if self.startpoints.data.shape != self.endpoints.data.shape:
            raise ValueError('Shapes of centers and endpoints do not match')
        else:
            return True

    def calculate_orientation_block(self, vector: np.ndarray):
        """
        Parameters
        -------
        vector : np.ndarray
                 A vector which you would like to align with the orientation vectors of each dipole

        Returns
        -------
        orientation_block : OrientationBlock
                            SimpleBlock containint rotation matrices which premultiply 'vector' to
                            align it with the orientation vectors of each dipole in this object
        """
        # only implemented for 3d rotations
        if self.startpoints.data.shape[1] != 3:
            raise NotImplementedError

        # force ndarray
        vector = np.asarray(vector).reshape(-1)

        # normalise vector
        normalised_vector = vector / np.linalg.norm(vector)

        # calculate rotation matrices
        rotation_matrices = align_vectors(normalised_vector, self.normalised_orientation_vectors)
        return OrientationBlock(rotation_matrices, parent=self)
