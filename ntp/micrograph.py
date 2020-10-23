import numpy as np
from eulerangles import euler2matrix


class Micrograph:
    """
    collects a micrograph and its related data
    """
    axes = ['x', 'y', 'z']

    def __init__(self, data_frame, name=''):
        self.name = name
        self.data = data_frame
        self._orient_matrix = None

        # add useful columns to the dataframe
        # x, y and z but normalized
        for axis in self.axes:
            self.data[axis] = self.data[f'rlnCoordinate{axis.upper()}'] + self.data.get(f'rlnOrigin{axis.upper()}', 0)

        self._calulate_orient_matrix()

    def coords(self, order='zyx'):
        """
        return requested coordinates as numpy array
        """
        if any([ax not in self.axes for ax in order.lower()]):
            raise Exception # TODO
        return self.data[[axis for axis in order.lower()]].to_numpy()

    def _calulate_orient_matrix(self):
        """
        transform orientation of particles from euler angles to rotation matrices
        """
        # these needs to be stored separately or we lose vectorization
        # how do we keep these updated? # TODO
        orient_euler = self.data[['rlnAngleRot', 'rlnAngleTilt', 'rlnAnglePsi']].to_numpy()
        self._orient_matrix = euler2matrix(orient_euler, axes='ZYZ', intrinsic=True, positive_ccw=True)

    def orient_matrix(self, order='zyx'):
        # needed because order is xyz from euler2matrix
        mapping = {'x': 0, 'y': 1, 'z': 2}
        idx = [mapping[axis] for axis in order]
        ax1 = self._orient_matrix[:, :, idx[0]]
        ax2 = self._orient_matrix[:, :, idx[1]]
        ax3 = self._orient_matrix[:, :, idx[2]]
        return np.stack((ax1, ax2, ax3), axis=2)

    def orient_vectors(self, scale=1, order='zyx'):
        """
        return a napari-compliant array of vectors representing the orientation of particles
        """
        vectors = np.einsum('ijk,j->ik', self.orient_matrix(), [0, 0, scale])

        return np.stack([self.coords(order), vectors], axis=1)
