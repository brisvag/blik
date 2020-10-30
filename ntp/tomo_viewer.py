import numpy as np
import napari

from utils import read_images, read_starfiles


class Viewable:
    """
    Base class for viewable object in napari
    """
    def __init__(self, viewer=None, parent=None, name='', *args, **kwargs):
        self.viewer = viewer
        self.parent = parent
        self.name = name

    def show(self, viewer=None, *args, **kwargs):
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
    def __init__(self, coordinates, orientation_vectors, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.coords = coordinates
        self.vectors = np.stack([coordinates, orientation_vectors], axis=1)

    def show(self, *args, **kwargs):
        v = super().show(*args, **kwargs)
        v.add_points(self.coords, name=f'{self.name} - particle positions', size=2)
        v.add_vectors(self.vectors, name=f'{self.name} - particle orientations')
        return v

    def update(self, *args, **kwargs):
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

    def show(self, *args, **kwargs):
        v = super().show(*args, **kwargs)
        v.add_image(self.data, name=f'{self.name} - image', scale=self.scale)
        return v

    def update(self, *args, **kwargs):
        self.viewer.layers.remove(f'{self.name} - image')
        self.show()


class TomoViewer(Viewable):
    """
    load and diosplay an arbitrary set of images and datasets
    """
    def __init__(self, mrc_paths=None, star_paths=None, stack=True, sort=True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.items = []

        star_dfs = read_starfiles(star_paths, sort)
        # for now, we can only show a perfect 1:1 ratio of images to starfiles TODO
        # this check must be done after loading starfiles, but better before images to stop early if needed
        if len(mrc_paths) != len(star_dfs):
            raise NotImplementedError('ratio of images:starfiles different from 1:1 not supported yet')
        images = read_images(mrc_paths, sort)

        # if stack is requested, prepare for that
        if stack:
            image_4d = np.stack(images)
            coords_4d = []
            vectors_4d = []

        # loop through everything
        for idx, (image, (name, coords, vectors)) in enumerate(zip(images, star_dfs)):
            # denormalize if necessary (not index column) by multiplying by the shape of images
            if coords.max() <= 1:
                coords *= image.shape
            if stack:
                n_coords = coords.shape[0]
                shape = (n_coords, 1)
                # add a leading, incremental coordinate to points and vectors that indicates the index
                # of the 4th dimension in which to show that volume
                coords_4d.append(np.concatenate([np.ones(shape) * idx, coords], axis=1))
                vectors_4d.append(np.concatenate([np.ones(shape) * idx, vectors], axis=1))
            else:
                self.items.append(Image(image, parent=self.parent, name=name, *args, **kwargs))
                self.items.append(Particles(coords, vectors, parent=self.parent, name=name, *args, **kwargs))
        if stack:
            # TODO: guess a good name for the whole stack
            # name = guess_name(mrc_paths)
            coords_4d = np.concatenate(coords_4d)
            vectors_4d = np.concatenate(vectors_4d)
            self.items.append(Image(image_4d, parent=self.parent, name='stack', *args, **kwargs))
            self.items.append(Particles(coords_4d, vectors_4d, parent=self.parent, name='stack', *args, **kwargs))

    def show(self, *args, **kwargs):
        v = super().show(*args, **kwargs)
        for item in self.items:
            item.show(viewer=v)
        return v

    def update(self, *args, **kwargs):
        for item in self.items:
            item.update(*args, **kwargs)
