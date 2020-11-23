### QUICK SUMMARY
# If you want to generate relion euler angles from matrices which align references to particles
# use:
# matrix2euler zyz intrinsic positive_ccw
# on the transpose of the matrix

# If you want to generate rotation matrices which align references onto aligned particles
# use:
# euler2matrix zyz intrinsic positive_ccw
# then transpose the matrix/matrices


# If you want to generate dynamo euler angles from matrices which align references to particles
# use:
# matrix2euler zxz intrinsic positive_ccw
# on the transpose of the matrix

# If you want to generate matrices which align references to particles from dynamo euler angles
# use:
# euler2matrix zxz extrinsic positive_ccw
# then transpose the matrix/matrices

import numpy as np
from eulerangles import matrix2euler, euler2matrix


class EulerAngleConvention:
    def __init__(self, axes: str, intrinsic: bool, positive_ccw: bool, rotate_reference: bool):
        """
        An object for storing information which we need for interpretation/generaton of Euler angles
        for a given software package in the context of cryo-EM/subtomogram averaging/SPA

        Parameters
        ----------
        axes : str
               three consecutive axes from ''x' 'y' and 'z'

        intrinsic : bool
                    True if angles represent intrinsic rotations (axes move with the object)
                    False if angles represent extrinsic rotations (axes do not move with the object)

        positive_ccw : bool
                       True if a positive angle means a counter clockwise rotation when looking at the origin from
                       a positive point along an axis
                       False otherwise

        rotate_reference : bool
                           True if the Euler angles define a rotation which rotates a reference onto a particle
                           False otherwise
        """
        self.axes = axes
        self.intrinsic = intrinsic
        self.positive_ccw = positive_ccw
        self.rotate_reference = rotate_reference


class EulerAngleHelper:
    """
    A helper class to facilitate dealing with Euler angles in their many conventions

    This class will always output rotation matrices which transform reference onto aligned particles

    This class will always output euler angles in the correct format for use within a given software package
    """

    def __init__(self, euler_angles: np.ndarray = None, rotation_matrices: np.ndarray = None):
        self.euler_angles = euler_angles
        self.rotation_matrices = rotation_matrices

    @property
    def modes(self):
        """
        List of supported modes for dealing with euler angles
        """
        return self._conventions.keys()

    @property
    def _conventions(self):
        """
        dict of supported Euler angle conventions
        """
        # Import here to avoid circular imports
        from ..constants.relion_constants import relion_euler_angle_convention
        from ..constants.dynamo_constants import dynamo_euler_angle_convention
        from ..constants.warp_constants import warp_euler_angle_convention

        conventions = {'relion': relion_euler_angle_convention,
                       'dynamo': dynamo_euler_angle_convention,
                       'warp': warp_euler_angle_convention}
        return conventions

    def get_convention(self, mode: str):
        mode = mode.strip().lower()
        if mode in self.modes:
            return self._conventions[mode]
        else:
            raise ValueError(f"Mode '{mode}' not in '{self.modes}'")

    @property
    def euler_angles(self):
        return self._euler_angles

    @euler_angles.setter
    def euler_angles(self, euler_angles: np.ndarray):
        if euler_angles is not None:
            self._euler_angles = np.asarray(euler_angles).reshape((-1, 3))
        else:
            self._euler_angles = euler_angles

    @property
    def rotation_matrices(self):
        return self._rotation_matrices

    @rotation_matrices.setter
    def rotation_matrices(self, rotation_matrices: np.ndarray):
        if rotation_matrices is not None:
            self._rotation_matrices = np.asarray(rotation_matrices).reshape((-1, 3, 3))
        else:
            self._rotation_matrices = rotation_matrices

    @staticmethod
    def invert_rotation_matrices(rotation_matrices: np.ndarray):
        """
        Inverts a set of rotation matrices by transposing the last two axes

        Parameters
        ----------
        rotation_matrices : (n, 3, 3) array of float
                            n rotation matrices

        Returns
        -------
        inverted_rotation_matrices
        """
        inverted_rotation_matrices = rotation_matrices.transpose((0, 2, 1))
        return inverted_rotation_matrices

    def euler2matrix(self, mode: str):
        """
        Converts a set of Euler angles from a piece of software (given by 'mode')
        into a set of rotation matrices which rotate unit vectors into the aligned particle reference frame

        Parameters
        ----------
        mode : str
               must be in self.modes

        Returns
        ----------
        rotation_matrices : (n, 3, 3) array of float
                            n rotation matrices which rotate unit vectors into the aligned particle reference frame
        """
        convention = self.get_convention(mode)

        # Convert euler angles to matrices
        rotation_matrices = euler2matrix(self.euler_angles,
                                         axes=convention.axes,
                                         intrinsic=convention.intrinsic,
                                         positive_ccw=convention.positive_ccw)

        # If rotation matrices represent rotations of particle onto reference
        # invert them so that we return matrices which transform reference onto particle
        if convention.rotate_reference is not True:
            rotation_matrices = self.invert_rotation_matrices(rotation_matrices)

        return rotation_matrices

    def matrix2euler(self, mode: str):
        """
        Converts a set of rotation matrices which rotate unit vectors into the aligned particle reference frame
        into a set of Euler angles from a piece of software (given by 'mode')
        Parameters
        ----------
        mode : str
               must be in self.modes
        Returns
        -------
        euler_angles : (n, 3) array of float
                       Euler angles which can be used for particle extraction/reconstruction
                       in the software given by 'mode'
        """
        convention = self.get_convention(mode)
        rotation_matrices = self.rotation_matrices

        # Do I need to invert my matrix first?
        if convention.rotate_reference is False:
            rotation_matrices = self.invert_rotation_matrices(rotation_matrices)

        # convert matrices to euler angles
        euler_angles = matrix2euler(rotation_matrices,
                                    target_axes=convention.axes,
                                    target_intrinsic=convention.intrinsic,
                                    target_positive_ccw=convention.positive_ccw)

        return euler_angles


