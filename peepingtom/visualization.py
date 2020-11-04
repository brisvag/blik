import numpy as np
import napari
import logging
from itertools import zip_longest

from utils import read_images, read_starfiles
import gui


log = logging.getLogger(__name__)
logging.basicConfig(level=logging.info)


class Viewable:
    """
    Base class for viewable object in napari
    """
    def __init__(self, viewer=None, parent=None, name=''):
        self.viewer = viewer
        self.parent = parent
        self.name = name
        self.layer = None

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

    def update(self, *args, **kwargs):
        """
        reload data in the viewer
        """
        self.viewer.layers.remove(self.layer)
        self.show(*args, **kwargs)

    def __repr__(self):
        if not self.name:
            name = 'NoName'
        else:
            name = self.name
        return f'<{type(self).__name__}-{name}>'


class ParticlesPositions(Viewable):
    def __init__(self, coordinates, properties=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.coords = coordinates
        self.properties = properties

    def show(self, viewer=None, points_kwargs={}):
        v = super().show(viewer=viewer)
        self.layer = v.add_points(self.coords, name=f'{self.name} - particle positions', size=2, properties=self.properties, **points_kwargs)
        return v


class ParticlesOrientations(Viewable):
    def __init__(self, vectors, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.vectors = vectors

    def show(self, viewer=None, vectors_kwargs={}):
        v = super().show(viewer=viewer)
        self.layer = v.add_vectors(self.vectors, name=f'{self.name} - particle orientations', **vectors_kwargs)
        return v


class Particles(Viewable):
    """
    represent positions and orientations of particles in a volume
    coordinates: (n, m+3), with m=additional spatial dimensions. Last 3 are in order zyx
    orientation_vectors: (n, m+3) as above, centered on the origin
    """
    def __init__(self, coordinates, orientation_vectors, properties=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.coords = ParticlesPositions(coordinates, properties, parent=self.parent, *args, **kwargs)
        proj_vectors = np.stack([coordinates, orientation_vectors], axis=1)
        self.vectors = ParticlesOrientations(proj_vectors, parent=self.parent, *args, **kwargs)

    def show(self, viewer=None, points=True, vectors=True, points_kwargs={}, vectors_kwargs={}):
        v = super().show(viewer=viewer)
        if points:
            self.coords.show(viewer, points_kwargs)
        if vectors:
            self.vectors.show(viewer, vectors_kwargs)
        return v

    def update(self):
        for l in [self.coords.layer, self.vectors.layer]:
            self.viewer.layers.remove(l)
        self.show()


class Image(Viewable):
    """
    ND image of shape (#m, z, y, x), with m additional dimensions
    image_scale: float or np array of shape (m+3,)
    """
    def __init__(self, data, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = data

    def show(self, viewer=None, image_kwargs={}):
        v = super().show(viewer=viewer)
        self.layer = v.add_image(self.data, name=f'{self.name} - image', **image_kwargs)
        return v


class Peeper(Viewable):
    """
    load and display an arbitrary set of images and/or datasets
    """
    def __init__(self, mrc_paths=None, star_paths=None, sort=True, data_columns=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.images = []
        self.particles = []
        self.stack_image = None
        self.stack_particles = None
        self.unmatching_data = False

        if star_paths is None:
            star_paths = []
        if mrc_paths is None:
            mrc_paths = []
        star_dfs = read_starfiles(star_paths, sort, data_columns)
        # this check must be done after loading starfiles, but better before images
        if not isinstance(mrc_paths, list):
            # needed for length check
            mrc_paths = [mrc_paths]
        if len(mrc_paths) != len(star_dfs):
            logging.warn('Number of datasets is different between images and starfiles!')
            self.unmatching_data = True
        images = read_images(mrc_paths, sort)

        # loop through everything
        for image, (name, coords, vectors, add_data) in zip_longest(images, star_dfs):
            if image is not None:
                self.images.append(Image(image, parent=self.parent, name=name, *args, **kwargs))
            # denormalize if necessary (not index column) by multiplying by the shape of images
            if coords is not None:
                if coords.max() <= 1 and self.unmatching_data:
                    coords *= image.shape
                self.particles.append(Particles(coords, vectors, parent=self.parent, name=name, properties=add_data, *args, **kwargs))

    def _make_stack(self):
        if self.images:
            image_4d = np.stack([img.data for img in self.images])
            self.stack_image = Image(image_4d, parent=self.parent, name='stack')
        if self.particles:
            coords_4d = []
            vectors_4d = []
            add_data_4d = {}
            for idx, prt in enumerate(self.particles):
                # get the length of coords as (n, 1) shape
                n_coords = prt.coords.shape[0]
                shape = (n_coords, 1)
                # add a leading, incremental coordinate to points that indicates the index
                # of the 4th dimension in which to show that volume
                coords_4d.append(np.concatenate([np.ones(shape) * idx, prt.coords], axis=1))
                # just zeros for vectors, cause they are projection vectors centered on the origin,
                # otherwise they would traverse the 4th dimension to another 3D slice
                vectors_4d.append(np.concatenate([np.zeros(shape), prt.vectors], axis=1))
                # loop through properties to stack them
                for k, v in prt.properties.items():
                    if k not in add_data_4d:
                        add_data_4d[k] = []
                    add_data_4d[k].append(v)
            # concatenate in one big array
            coords_4d = np.concatenate(coords_4d)
            vectors_4d = np.concatenate(vectors_4d)
            for k, v in add_data_4d.items():
                add_data_4d[k] = np.concatenate(v)
            self.stack_particles = Particles(coords_4d, vectors_4d, parent=self.parent, name='stack', properties=add_data_4d)

    def show(self, viewer=None, points_kwargs={}, vectors_kwargs={}, image_kwargs={}, stack=True):
        v = super().show(viewer=viewer)
        if stack:
            if self.stack_image is None and self.stack_particles is None:
                self._make_stack()
            if self.stack_image:
                self.stack_image.show(viewer=v, image_kwargs=image_kwargs)
            if self.stack_particles:
                self.stack_particles.show(viewer=v, points_kwargs=points_kwargs, vectors_kwargs=vectors_kwargs)
        else:
            for image in self.images:
                image.show(viewer=v, image_kwargs=image_kwargs)
            for particles in self.particles:
                particles.show(viewer=v, points_kwargs=points_kwargs, vectors_kwargs=vectors_kwargs)
        return v

    def update(self):
        for item in self.particles + self.images:
            item.update()
