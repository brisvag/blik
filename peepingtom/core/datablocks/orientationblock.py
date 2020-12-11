import numpy as np
from eulerangles import euler2matrix

from .base import SimpleBlock


class OrientationBlock(SimpleBlock):
    """
    OrientationBlock objects represent orientations in a 2d or 3d space

    Contains factory methods for instantiation from eulerian angles

    rotation_matrices : (n, 2, 2) or (n, 3, 3) array of rotation matrices R
                        R should satisfy Rv = v' where v is a column vector

    """
    def _data_setter(self, data: np.ndarray):
        data = np.array(data)
        # check for single matrix case and assert dimensionality
        val_error = ValueError(f'rotation matrices should be of shape '
                               f'(2, 2), (3, 3), (n, 2, 2) or (n, 3, 3), '
                               f'not {data.shape}')
        if data.ndim == 1:
            raise val_error
        if not data.shape[-1] == data.shape[-2]:
            raise val_error
        if not data.shape[-1] in (2, 3):
            raise val_error

        if data.ndim == 2:
            m = data.shape[-1]
            data = data.reshape((1, m, m))

        return data

    @property
    def n(self):
        return len(self)

    @property
    def ndim(self):
        """
        as ndim for numpy arrays, but treating the vectors as a sparse matrix.
        returns the number of dimensions (spatial or not) describing the vectors
        """
        return self.data.shape[-1]

    @classmethod
    def from_euler_angles(cls, euler_angles: np.ndarray, axes: str, intrinsic: bool, positive_ccw: bool,
                          invert_matrix: bool):
        """
        Factory method for creating a VectorBlock directly from a set of eulerian angles

        Parameters
        ----------
        euler_angles : ndarray, (n, 3) array of n sets of eulerian angles in degrees
        axes : str, 3 characters from 'x', 'y' and 'z' representing axes around which rotations
               occur in the euler angles
        intrinsic : bool, are the euler angles describing a set of intrinsic (rotating reference frame)
                    or extrinsic (fixed reference frame) rotations
        positive_ccw : bool, are positive euler angles referring to counterclockwise rotations of vectors
                       when looking from a positive point along the axis towards the origin
        invert_matrix : bool, should the matrix be inverted?
                        this is useful if your euler angles describe the rotation of a target to a source
                        but you would like your rotation matrices to describe the rotation of a source to
                        align it with a target

        Returns
        -------

        """
        # Calculate rotation matrices
        rotation_matrices = euler2matrix(euler_angles, axes=axes, intrinsic=intrinsic,
                                         positive_ccw=positive_ccw)

        # invert matrix if required
        if invert_matrix:
            rotation_matrices = rotation_matrices.transpose((-1, -2))

        return cls(rotation_matrices)

    def _calculate_matrix_product(self, vector: np.ndarray):
        """
        Calculates the matrix product (v') of the orientation matrices (R) in this
        VectorBlock object with a given vector (v)
        Rv = v'

        Parameters
        ----------
        vector : ndarray v, column vector or set of column vectors to be premultiplied by rotation matrices

        Returns ndarray v', matrix product Rv
        -------

        """
        return self.data @ vector

    def _unit_vector(self, axis: str):
        """
        Get a unit vector along a specified axis which matches the dimensionality of the VectorBlock object

        Parameters
        ----------
        axis : str, named axis 'x', 'y' or 'z'

        Returns unit vector along provided axis with appropriate dimensionality
        -------

        """
        # check dimensionality
        if self.ndim > 3:
            raise NotImplementedError('Unit vector generation for objects with greater '
                                      'than 3 spatial dimensions is not implemented')

        # initialise unit vector array
        unit_vector = np.zeros((self.ndim, 1))

        # get index which corresponds to axis for vector
        axis_to_index = {'x': 0,
                         'y': 1,
                         'z': 2}
        dim_idx = axis_to_index[axis]

        # construct unit vector
        if dim_idx <= self.ndim:
            unit_vector[dim_idx, 0] = 1
        else:
            raise ValueError(f"You asked for axis {axis} from a {self.ndim}d object")

        return unit_vector

    def oriented_vectors(self, axis):
        return self._calculate_matrix_product(self._unit_vector(axis))

    def dump(self):
        kwargs = super().dump()
        kwargs.update({'orientation_block': self.data})
        return kwargs

    @staticmethod
    def _merge_data(datablocks):
        return np.concatenate([db.data for db in datablocks])

    @staticmethod
    def _stack_data(datablocks):
        return np.concatenate([db.data for db in datablocks])

    def __shape_repr__(self):
        return f'({self.n}, {self.ndim})'
