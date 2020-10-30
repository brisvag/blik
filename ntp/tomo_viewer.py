import re
from pathlib import Path
import numpy as np
import napari
import starfile
from eulerangles import euler2matrix

from utils import read_images, read_starfiles


class Viewable:
    """
    Base class for viewable object in napari
    """
    def __init__(self, viewer=None, parent=None, name='', *args, **kwargs):
        self.viewer = viewer
        if parent is None:
            parent = self
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
    coordinates: (n, 3), in napari format zyx
    orientation_vectors: (n, 3), in napari format zyx centered on the origin
    """
    def __init__(self, coordinates, orientation_vectors, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.coords = coordinates
        self.vectors = np.stack([coordinates, orientation_vectors], axis=1)

    def show(self, *args, **kwargs):
        v = super().show(*args, **kwargs)
        v.add_points(self.coords, name=f'{self.parent.name} - particle positions', size=2)
        v.add_vectors(self.vectors, name=f'{self.parent.name} - particle orientations')
        return v

    def update(self, *args, **kwargs):
        self.viewer.layers.remove(f'{self.parent.name} - particle positions')
        self.viewer.layers.remove(f'{self.parent.name} - particle orientations')
        self.show()


class Image(Viewable):
    """
    3d image in napari format zyx
    image_scale: float or np array of shape (3,)
    """
    def __init__(self, data, image_scale=1, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = data
        self.shape = self.data.shape
        self.scale = (self.data.ndim * [1]) * np.array(image_scale)

    def show(self, *args, **kwargs):
        v = super().show(*args, **kwargs)
        v.add_image(self.data, name=f'{self.parent.name} - image', scale=self.scale)
        return v

    def update(self, *args, **kwargs):
        self.viewer.layers.remove(f'{self.parent.name} - image')
        self.show()


class TomoViewer(Viewable):
    """
    load and diosplay an arbitrary set of images and datasets
    """
    def __init__(self, mrc_paths=None, star_paths=None, stack=True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.items = []

        images = read_images(mrc_paths)
        star_dfs = read_starfiles(star_paths)

        # for now, we can only show a perfect 1:1 ratio of images to starfiles TODO
        if len(images) != len(star_dfs):
            raise NotImplementedError('ratio of images:starfiles different from 1:1 not supported yet')

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
                self.items.append(Image(image, parent=self.parent, *args, **kwargs))
                self.items.append(Particles(coords, vectors, parent=self.parent, *args, **kwargs))
        if stack:
            coords_4d = np.concatenate(coords_4d)
            vectors_4d = np.concatenate(vectors_4d)
            self.items.append(Image(image_4d, parent=self.parent, *args, **kwargs))
            self.items.append(Particles(coords_4d, vectors_4d, parent=self.parent, *args, **kwargs))
        # if stack:
            # # show as 4D stack of volumes
            # image_4d = np.stack(images)
            # coords_4d = []
            # vectors_4d = []
            # for idx, (_, coords, vectors) in enumerate(star_dfs):
                # n_coords = coords.shape[0]
                # shape = (n_coords, 1)
                # # add a leading, incremental coordinate to points and vectors that indicates the index
                # # of the 4th dimension in which to show that volume
                # coords_4d.append(np.concatenate([np.ones(shape) * idx, coords], axis=1))
                # vectors_4d.append(np.concatenate([np.ones(shape) * idx, vectors], axis=1))
            # # stack them up
            # coords_4d = np.concatenate(coords_4d)
            # vectors_4d = np.concatenate(vectors_4d)
            # # denormalize if necessary (not index column) by multiplying by the shape of images
            # # TODO: we now assume images are all the same size!
            # if coords.max() <= 1:
                # coords_4d[:,1:] *= image_4d.shape[1:]
            # self.images.append(Image(image_4d, parent=self.parent, *args, **kwargs))
            # self.particles.append(Particles(coords_4d, vectors_4d, parent=self.parent, *args, **kwargs))
        # else:
            # # create individual particles and images to show as layers
            # for image, (name, coords, vectors) in zip(images, star_dfs):
                # self.images.append
                # self.tws.append(TomoViewer(mrc, star_df, name=name, *args, **kwargs))
            # else:
                # df = starfile.read(star_paths)
                # groups = df.groupby('rlnMicrographName')
                # if len(groups) == len(mrc_paths):
                    # for mrc, (mg_name, star_df) in zip(mrc_paths, groups):
                        # name = self._get_name(mg_name)
                        # self.tws.append(TomoViewer(mrc, star_df, name=name, *args, **kwargs))
                # else:
                    # raise ValueError('a different number of .mrc and .star files was found. Aborting...')
        # if isinstance(star_paths, list):
            # raise ValueError('a different number of .mrc and .star files was found. Aborting...')
        # else:
            # name = self._get_name(mrc_paths)
            # star_df = starfile.read(_path(star_paths))
            # self.tws.append(TomoViewer(mrc_paths, star_df, name=name, *args, **kwargs))

    def show(self, *args, **kwargs):
        v = super().show(*args, **kwargs)
        for item in self.items:
            item.show(viewer=v)
        return v

# class TomoViewer(Viewable):
    # """
    # Image and data associated with a single volume
    # """
    # def __init__(self, mrc_path=None, star_df=None, *args, **kwargs):
        # super().__init__(*args, **kwargs)
        # self.image = None
        # self.particles = None

        # if mrc_path is not None:
            # self.image = Image(mrc_path, parent=self.parent, *args, **kwargs)

        # if star_df is not None:
            # star_df = self._cutoff_df(star_df, 'rlnAutopickFigureOfMerit', '>', 20)
            # # get coordinates from dataframe in zyx order
            # coords = []
            # for axis in 'ZYX':
                # ax = np.array(star_df[f'rlnCoordinate{axis}'] + star_df.get(f'rlnOrigin{axis}', 0))
                # coords.append(ax)
            # coords = np.stack(coords, axis=1)
            # # de-normalize if needed
            # if coords.max() <= 1 and self.image is not None:
                # coords = coords * self.image.shape

            # # get orientations as euler angles and transform it into rotation matrices
            # orient_euler = star_df[['rlnAngleRot', 'rlnAngleTilt', 'rlnAnglePsi']].to_numpy()
            # orient_matrices = euler2matrix(orient_euler, axes='ZYZ', intrinsic=True, positive_ccw=True)
            # # get orientations as unit vectors centered on the origin
            # orient_vectors = np.einsum('ijk,j->ik', orient_matrices, [0, 0, 1])
            # # reslice them in zyx order
            # orient_vectors = orient_vectors[:, [2, 1, 0]]

            # self.particles = Particles(coords, orient_vectors, parent=self.parent, *args, **kwargs)

    # @staticmethod
    # def _cutoff_df(df, column, criterion, cutoff):
        # if criterion == '>':
            # return df[df[column] >= cutoff]
        # elif criterion == '<':
            # return df[df[column] <= cutoff]

    # def show(self, *args, **kwargs):
        # v = super().show(*args, **kwargs)
        # self.image.show(viewer=v)
        # self.particles.show(viewer=v)
        # return v

    # def update(self, *args, **kwargs):
        # self.image.update()
        # self.particles.update()


# class TWContainer(Viewable):
    # """
    # load and display several volumes and their relative starfile data
    # """
    # def __init__(self, mrc_paths=None, star_paths=None, as_stack=True, *args, **kwargs):
        # super().__init__(*args, **kwargs)

        # self.tws = []
        # if isinstance(mrc_paths, list):
            # if isinstance(star_paths, list):
                # # two lists are found: match them as they are found
                # for mrc, star in zip(mrc_paths, star_paths):
                    # star_df = starfile.read(_path(star))
                    # name = self._get_name(mrc)
                    # self.tws.append(TomoViewer(mrc, star_df, name=name, *args, **kwargs))
            # else:
                # df = starfile.read(star_paths)
                # groups = df.groupby('rlnMicrographName')
                # if len(groups) == len(mrc_paths):
                    # for mrc, (mg_name, star_df) in zip(mrc_paths, groups):
                        # name = self._get_name(mg_name)
                        # self.tws.append(TomoViewer(mrc, star_df, name=name, *args, **kwargs))
                # else:
                    # raise ValueError('a different number of .mrc and .star files was found. Aborting...')
        # elif isinstance(star_paths, list):
            # raise ValueError('a different number of .mrc and .star files was found. Aborting...')
        # else:
            # name = self._get_name(mrc_paths)
            # star_df = starfile.read(_path(star_paths))
            # self.tws.append(TomoViewer(mrc_paths, star_df, name=name, *args, **kwargs))

    # @staticmethod
    # def _get_name(path_or_string):
        # if match := re.search('TS_\d+', str(path_or_string)):
            # return match.group(0)
        # return False

    # @classmethod
    # def from_dirs(cls, mrc_dir, star_dir, mrc_pattern=None, star_pattern=None, *args, **kwargs):
        # mrcd = _path(mrc_dir)
        # stard = _path(star_dir)

        # mrc_list = []
        # for path in mrcd.glob('*.mrc'):
            # if mrc_pattern is not None:
                # if re.search(mrc_pattern, str(path)):
                    # mrc_list.append(path)
            # else:
                # mrc_list.append(path)
        # mrc_list = sorted(mrc_list)
        # if len(mrc_list) == 1:
            # mrc_list = mrc_list[0]

        # star_list = []
        # for path in stard.glob('*.star'):
            # if star_pattern is not None:
                # if re.search(star_pattern, str(path)):
                    # star_list.append(path)
            # else:
                # star_list.append(path)
        # star_list = sorted(star_list)
        # if len(star_list) == 1:
            # star_list = star_list[0]

        # return cls(mrc_list, star_list, *args, **kwargs)

    # @classmethod
    # def from_dir(cls, dir_path, pattern=None, *args, **kwargs):
        # return cls.from_dirs(dir_path, dir_path, mrc_pattern=pattern, star_pattern=pattern, *args, **kwargs)

    # def show(self, *args, **kwargs):
        # v = super().show(*args, **kwargs)
        # if self.as_stack:
            # for tw in self.tws:
                # pass
        # else:
            # for tw in self.tws:
                # tw.show(viewer=v)
        # return v

    # def update(self, *args, **kwargs):
        # for tw in self.tws:
            # tw.update()
