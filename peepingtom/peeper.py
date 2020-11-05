from itertools import zip_longest
from utils import read_images, read_starfiles

from visualization import Viewable, ParticleViewer, ImageViewer


class Peeper(Viewable):
    """
    load and display an arbitrary set of images and/or datasets
    """
    def __init__(self, mrc_paths=None, star_paths=None, sort=True, data_columns=None, *args, **kwargs):
        self.volumes = []
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
                coords = prt.coords.coords
                vectors = prt.vectors.vectors
                properties = prt.coords.properties
                # get the length of coords as (n, 1) shape
                n_coords = coords.shape[0]
                shape = (n_coords, 1)
                # add a leading, incremental coordinate to points that indicates the index
                # of the 4th dimension in which to show that volume
                coords_4d.append(np.concatenate([np.ones(shape) * idx, coords], axis=1))
                # just zeros for vectors, cause they are projection vectors centered on the origin,
                # otherwise they would traverse the 4th dimension to another 3D slice
                vectors_4d.append(np.concatenate([np.zeros(shape), vectors], axis=1))
                # loop through properties to stack them
                for k, v in properties.items():
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
