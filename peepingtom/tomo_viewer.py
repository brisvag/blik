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
        self.vectors = orientation_vectors

    def show(self, viewer=None, points=True, vectors=True, points_kwargs={}, vectors_kwargs={}):
        v = super().show(viewer=viewer)
        if points:
            v.add_points(self.coords, name=f'{self.name} - particle positions', size=2, properties=self.properties, **points_kwargs)
        if vectors:
            proj_vectors = np.stack([self.coords, self.vectors], axis=1)
            v.add_vectors(proj_vectors, name=f'{self.name} - particle orientations', **vectors_kwargs)
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
    def __init__(self, mrc_paths=None, star_paths=None, sort=True, data_columns=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.images = []
        self.particles = []
        self.stack = {}
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
            self.stack['images'] = Image(image_4d, parent=self.parent, name='stack')
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
            self.stack['particles'] = Particles(coords_4d, vectors_4d, parent=self.parent, name='stack', properties=add_data_4d)

    def show(self, viewer=None, points_kwargs={}, vectors_kwargs={}, image_kwargs={}, stack=True):
        v = super().show(viewer=viewer)
        if stack:
            if not self.stack:
                self._make_stack()
            if 'images' in self.stack:
                self.stack['images'].show(viewer=v, image_kwargs=image_kwargs)
            if 'particles' in self.stack:
                self.stack['particles'].show(viewer=v, points_kwargs=points_kwargs, vectors_kwargs=vectors_kwargs)
        else:
            for image in self.images:
                image.show(viewer=v, image_kwargs=image_kwargs)
            for particles in self.particles:
                particles.show(viewer=v, points_kwargs=points_kwargs, vectors_kwargs=vectors_kwargs)
        return v

    def update(self):
        for item in self.particles + self.images:
            item.update()
