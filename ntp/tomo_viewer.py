import numpy as np
import napari
from eulerangles import euler2matrix


def tomoviewer_factory(mrc_path=None, star_df=None, viewer=None):
    image = None
    if mrc_path is not None:
        image = Image(mrc_path)

    particles = None
    if star_df is not None:
        # get coordinates from dataframe in zyx order
        coords = []
        for axis in 'ZYX':
            ax = np.array(star_df[f'rlnCoordinate{axis}'] + star_df.get(f'rlnOrigin{axis}', 0))
            coords.append(ax)
        coords = np.stack(coords, axis=1)
        # de-normalize if needed
        if coords.max() <= 1:
            coords = coords * image.shape

        # get orientations as euler angles and transform it into rotation matrices
        orient_euler = star_df[['rlnAngleRot', 'rlnAngleTilt', 'rlnAnglePsi']].to_numpy()
        orient_matrices = euler2matrix(orient_euler, axes='ZYZ', intrinsic=True, positive_ccw=True)
        # get orientations as unit vectors centered on the origin
        orient_vectors = np.einsum('ijk,j->ik', orient_matrices, [0, 0, 1])
        # reslice them in zyx order
        orient_vectors = orient_vectors[:, [2,1,0]]

        particles = Particles(coords, orient_vectors)

    return TomoViewer(image, particles, viewer)


class Particles:
    """
    represent positions and orientations of particles in a volume
    coordinates: (n, 3), in napari format zyx
    orientation_vectors: (n, 3), in napari format zyx centered on the origin
    """
    def __init__(self, coordinates, orientation_vectors):
        self.coords = coordinates
        self.vectors = np.stack([coordinates, orientation_vectors], axis=1)


class Image:
    """
    3d image in napari format zyx
    """
    def __init__(self, image_path):
        self.data = napari.plugins.io.read_data_with_plugins(image_path)[0][0]
        self.shape = self.data.shape


class TomoViewer:
    def __init__(self, image=None, particles=None, viewer=None):
        self.image = image
        self.particles = particles
        self.viewer = viewer

    def show(self, viewer=None):
        # create a new viewer if none was ever passed
        if viewer is not None:
            v = viewer
        elif self.viewer is None:
            v = napari.Viewer(ndisplay=3)
        else:
            v = self.viewer

        if self.image is not None:
            v.add_image(self.image.data)
        if self.particles is not None:
            v.add_points(self.particles.coords)
            v.add_vectors(self.particles.vectors)
        return v


class TomoViewerWarp(TomoViewer):
    def __init__(mrc_path=None, star_df=None, viewer=None):
        image = None
        if mrc_path is not None:
            image = Image(mrc_path)

        particles = None
        if star_df is not None:
            # get coordinates from dataframe in zyx order
            coords = []
            for axis in 'ZYX':
                ax = np.array(star_df[f'rlnCoordinate{axis}'] + star_df.get(f'rlnOrigin{axis}', 0))
                coords.append(ax)
            coords = np.stack(coords, axis=1)
            # de-normalize if needed
            if coords.max() <= 1:
                coords = coords * image.shape

            # get orientations as euler angles and transform it into rotation matrices
            orient_euler = star_df[['rlnAngleRot', 'rlnAngleTilt', 'rlnAnglePsi']].to_numpy()
            orient_matrices = euler2matrix(orient_euler, axes='ZYZ', intrinsic=True, positive_ccw=True)
            # get orientations as unit vectors centered on the origin
            orient_vectors = np.einsum('ijk,j->ik', orient_matrices, [0, 0, 1])
            # reslice them in zyx order
            orient_vectors = orient_vectors[:, [2,1,0]]

            particles = Particles(coords, orient_vectors)

        super().__init__(image, particles, viewer)


class BatchTomoViewer:
    def __init__(self, viewer=None):
        self.viewer = viewer
        self.tomoviewers = []

    def show(self, viewer=None):
        if viewer is not None:
            v = viewer
        elif self.viewer is None:
            v = napari.Viewer(ndisplay=3)
        else:
            v = self.viewer

        images = np.stack([tw.image.data for tw in self.tomoviewers])
        coords = np.stack([tw.particles.coords for tw in self.tomoviewers])
        vectors = np.stack([tw.particles.vectors for tw in self.tomoviewers])

        if images is not None:
            v.add_image(images)
        if self.particles is not None:
            v.add_points(coords)
            v.add_vectors(vectors)
        return v


class TomoViewerOld:
    """
    base class for handling images and cropping geometries
    """
    def __init__(self, image, coords, vectors):
        self.name = name
        self._data = data_frame
        self.image = None
        self._coords = self._get_coords()
        self._orientation_matrix = self._get_orientation_matrix()
        self._vectors = self._get_orientation_vectors()
        if mrc_path:
            self.get_image(mrc_path)

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

    def get_image(self, mrc_path):
        self.image = napari.plugins.io.read_data_with_plugins(mrc_path)[0][0]

    def coords(self, order='zyx', normalize=False):
        """
        return coordinates as numpy array in the requested order
        if normalize is set, coordinates are assumed to be between 0 and 1 and are
        multiplied by the shape of the image
        """
        mapping = self._map_axes(order)
        dimensions = (1, 1, 1)
        if normalize and self.image is not None:
            dimensions = self.image.shape
        return self._coords[:, mapping] * dimensions

    def vectors(self, order='zyx', normalize=False):
        """
        return a napari-compliant array of vectors representing the orientation of particles
        """
        return np.stack([self.coords(order, normalize=normalize), self._vectors[:, self._map_axes(order)]], axis=1)

    def view(self, image_scale=[1, 1, 1], v_length=20, coords_scale=[1, 1, 1], normalize=False):
        """
        open napari viewer with everything loaded
        """
        v = napari.Viewer(ndisplay=3)
        v.add_image(self.image, scale=image_scale)
        v.add_points(self.coords(normalize=normalize), scale=coords_scale, size=2)
        v.add_vectors(self.vectors(normalize=normalize), length=v_length)
        return v
