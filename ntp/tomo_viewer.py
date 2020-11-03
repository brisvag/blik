import numpy as np
import napari

from utils import read_images, read_starfiles
import gui


class Viewable:
    """
    Base class for viewable object in napari
    """
    def __init__(self, viewer=None, parent=None, name=''):
        self.viewer = viewer
        self.parent = parent
        self.name = name

    def show(self, viewer=None):
        """
        creates a new napari viewer if not present or given
        shows the contents of the Viewable
        """
        # create a new viewer if necessary
        if viewer is not None:
            self.viewer = viewer
        elif self.viewer is None:
            self.viewer = napari.Viewer(ndisplay=3)
        return self.viewer

    def update(self):
        """
        reload data in the viewer
        """

    def __repr__(self):
        if not self.name:
            name = 'NoName'
        else:
            name = self.name
        return f'<{type(self).__name__}-{name}>'


class Particles(Viewable):
    """
    represent positions and orientations of particles in a volume
    coordinates: (n, m+3), with m=additional spatial dimensions. Last 3 are in order zyx
    orientation_vectors: (n, m+3) as above, centered on the origin
    """
    def __init__(self, coordinates, orientation_vectors, properties=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.coords = coordinates
        self.properties = properties
        self.vectors = np.stack([coordinates, orientation_vectors], axis=1)

    def show(self, viewer=None, points=True, vectors=True, points_kwargs={}, vectors_kwargs={}):
        v = super().show(viewer=viewer)
        if points:
            v.add_points(self.coords, name=f'{self.name} - particle positions', size=2, properties=self.properties, **points_kwargs)
        if vectors:
            v.add_vectors(self.vectors, name=f'{self.name} - particle orientations', **vectors_kwargs)
        return v

    def update(self):
        self.viewer.layers.remove(f'{self.name} - particle positions')
        self.viewer.layers.remove(f'{self.name} - particle orientations')
        self.show()


class Image(Viewable):
    """
    ND image of shape (#m, z, y, x), with m additional dimensions
    image_scale: float or np array of shape (m+3,)
    """
    def __init__(self, data, image_scale=1, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = data
        self.shape = self.data.shape
        self.scale = (self.data.ndim * [1]) * np.array(image_scale)

    def show(self, viewer=None, image_kwargs={}):
        v = super().show(viewer=viewer)
        v.add_image(self.data, name=f'{self.name} - image', scale=self.scale, **image_kwargs)
        return v

    def update(self):
        self.viewer.layers.remove(f'{self.name} - image')
        self.show()


class TomoViewer(Viewable):
    """
    load and diosplay an arbitrary set of images and datasets
    """
    def __init__(self, mrc_paths=None, star_paths=None, stack=False, sort=True, data_columns=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.images = []
        self.particles = []

        star_dfs = read_starfiles(star_paths, sort, data_columns)
        # for now, we can only show a perfect 1:1 ratio of images to starfiles TODO
        # this check must be done after loading starfiles, but better before images to stop early if needed
        if not isinstance(mrc_paths, list):
            # needed for length check
            mrc_paths = [mrc_paths]
        if len(mrc_paths) != len(star_dfs):
            raise NotImplementedError('ratio of images:starfiles different from 1:1 not supported yet')
        images = read_images(mrc_paths, sort)

        # if stack is requested, prepare for that
        if stack:
            image_4d = np.stack(images)
            coords_4d = []
            vectors_4d = []
            # TODO: data in stack mode?

        # loop through everything
        for idx, (image, (name, coords, vectors, add_data)) in enumerate(zip(images, star_dfs)):
            # denormalize if necessary (not index column) by multiplying by the shape of images
            if coords.max() <= 1:
                coords *= image.shape
            if stack:
                # get the length of coords as (n, 1) shape
                n_coords = coords.shape[0]
                shape = (n_coords, 1)
                # add a leading, incremental coordinate to points that indicates the index
                # of the 4th dimension in which to show that volume
                coords_4d.append(np.concatenate([np.ones(shape) * idx, coords], axis=1))
                # just zeros for vectors, cause they are projection vectors centered on the origin,
                # otherwise they would traverse the 4th dimension to another 3D slice
                vectors_4d.append(np.concatenate([np.zeros(shape), vectors], axis=1))
            else:
                self.images.append(Image(image, parent=self.parent, name=name, *args, **kwargs))
                self.particles.append(Particles(coords, vectors, parent=self.parent, name=name, properties=add_data, *args, **kwargs))
        if stack:
            # TODO: guess a good name for the whole stack
            # name = guess_name(mrc_paths)
            coords_4d = np.concatenate(coords_4d)
            vectors_4d = np.concatenate(vectors_4d)
            self.images.append(Image(image_4d, parent=self.parent, name='stack', *args, **kwargs))
            self.particles.append(Particles(coords_4d, vectors_4d, parent=self.parent, name='stack', *args, **kwargs))

    def show(self, viewer=None, points_kwargs={}, vectors_kwargs={}, image_kwargs={}):
        v = super().show(viewer=viewer)
        for image, particles in zip(self.images, self.particles):
            image.show(viewer=v, image_kwargs=image_kwargs)
            particles.show(viewer=v, points_kwargs=points_kwargs, vectors_kwargs=vectors_kwargs)
        return v

    def update(self):
        for item in self.particles + self.images:
            item.update()
