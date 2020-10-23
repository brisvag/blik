import numpy as np
import napari
from eulerangles import euler2matrix


class Micrograph:
    """
    collects a micrograph and its related data
    """
    def __init__(self, data_frame, mrc_path=None, name=''):
        self.name = name
        self._data = data_frame
        self.mg = None
        self._coords = self._get_coords()
        self._orientation_matrix = self._get_orientation_matrix()
        self._vectors = self._get_orientation_vectors()
        if mrc_path:
            self.get_micrograph(mrc_path)

    def _get_coords(self):
        """
        extract normalized coords as np array for quicker access
        """
        coords = []
        for axis in 'XYZ':
            ax = np.array(self._data[f'rlnCoordinate{axis}'] + self._data.get(f'rlnOrigin{axis}', 0))
            coords.append(ax)
        return np.stack(coords, axis=1)

    @staticmethod
    def _map_axes(axes_str):
        """
        return correct index mapping as list from string of axes
        assuming slicing from array of shape (n,3) in xyz order
        """
        if any([ax not in 'xyz' for ax in axes_str.lower()]):
            raise Exception
        mapping = {'x': 0, 'y': 1, 'z': 2}
        return [mapping[ax] for ax in axes_str.lower()]

    def _get_orientation_matrix(self):
        """
        transform orientation of particles from euler angles to rotation matrices
        """
        orient_euler = self._data[['rlnAngleRot', 'rlnAngleTilt', 'rlnAnglePsi']].to_numpy()
        return euler2matrix(orient_euler, axes='ZYZ', intrinsic=True, positive_ccw=True)

    def _get_orientation_vectors(self):
        """
        transform rotation matrices into an array of unit vectors centered on the origin
        """
        return np.einsum('ijk,j->ik', self._orientation_matrix, [0, 0, 1])

    def get_micrograph(self, mrc_path):
        self.mg = napari.plugins.io.read_data_with_plugins(mrc_path)[0][0]

    def coords(self, order='zyx'):
        """
        return coordinates as numpy array in the requested order
        """
        return self._coords[:, self._map_axes(order)]

    def vectors(self, order='zyx'):
        """
        return a napari-compliant array of vectors representing the orientation of particles
        """
        return np.stack([self.coords(order), self._vectors[:, self._map_axes(order)]], axis=1)

    def view(self, mg_scale=[1,1,1], v_length=20, coords_scale=[1,1,1]):
        """
        open napari viewer with everything loaded
        """
        v = napari.Viewer(ndisplay=3)
        v.add_image(self.mg, scale=mg_scale)
        v.add_points(self.coords(), scale=coords_scale)
        v.add_vectors(self.vectors(), length=v_length)
        return v
