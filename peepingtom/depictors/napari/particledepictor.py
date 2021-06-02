import numpy as np
import xarray as xr
from skimage.measure import marching_cubes

from .naparidepictor import NapariDepictor
from ...utils.colors import distinct_colors


class ParticleDepictor(NapariDepictor):
    def __init__(self, datablock):
        super().__init__(datablock)
        self.rescale = 1

    def set_rescale(self):
        pos = self.datablock.positions.data
        if 0 <= pos.min().item() <= pos.max().item() <= 1:
            peeper = self.datablock.peeper
            if peeper and self.datablock.volume is not None:
                same_volume = peeper.volumes[self.datablock.volume]
                from ...datablocks import ImageBlock
                for db in same_volume:
                    if isinstance(db, ImageBlock):
                        self.rescale = db.shape
                        break

    def get_positions(self, rescale=True):
        if rescale:
            self.set_rescale()
        return self.datablock.positions.zyx * self.rescale * self.datablock.pixel_size


class ParticlePointDepictor(ParticleDepictor):
    """
    depict particles as points and vectors
    """
    def __init__(self, datablock):
        super().__init__(datablock)
        self.point_size = 40
        self.point_color = 'cornflowerblue'
        self.point_edge_color = 'black'
        self.vector_lengths = dict(z=150, y=75, x=75)
        self.vector_widths = dict(z=15, y=15, x=15)
        self.vector_colors = dict(
            z='darkblue',
            y='purple',
            x='green',
        )

    def depict(self):
        pos = self.get_positions()
        self._make_points_layer(pos,
                                name=f'{self.name} - particle positions',
                                properties=self.datablock.properties.data,
                                face_color=self.point_color,
                                size=self.point_size,
                                edge_color=self.point_edge_color,
                                )

        for ax, vectors in self.get_vectors().items():
            # need to use .values cause napari complains
            self._make_vectors_layer(vectors,
                                     name=f'{self.name} - particle orientations ({ax})',
                                     edge_color=self.vector_colors[ax],
                                     length=self.vector_lengths[ax],
                                     edge_width=self.vector_widths[ax],
                                     )

    def get_vectors(self):
        pos = self.get_positions()
        all_vectors = self.datablock.orientations.zyx_vectors()
        stacked = {}
        for ax, vectors in all_vectors.items():
            vec = xr.concat([pos, vectors], 'v').transpose('n', 'v', 'spatial').values
            stacked[ax] = vec
        return stacked

    @property
    def points(self):
        return self.layers[0]

    @property
    def vectors(self):
        return self.layers[1:]

    def color_by_categorical_property(self, property, colors=None):
        if self.layers:
            self.points.face_color = property
            self.points.face_color_cycle = colors or distinct_colors

    def update(self):
        if self.layers:
            pos = self.get_positions()
            self.points.data = pos.values  # workaround for xarray
            self.points.properties = self.datablock.properties.data

            vectors = self.get_vectors().values()
            for layer, vector in zip(self.vectors, vectors):
                layer.data = vector


class ParticleMeshDepictor(ParticleDepictor):
    """
    depict particles as isosurface meshes based on an input volume
    volume: if not an ImageBlock or a xarray, axis order must be zyx
    """
    def __init__(self, datablock, *, volume, iso=None, step_size=1):
        super().__init__(datablock)
        self.volume = volume
        self.iso = iso
        self.step_size = step_size
        self.mesh_color = 'cornflowerblue'

    def depict(self):
        vertices, faces = self.make_volume_mesh()
        all_vertices, all_faces = self.tile_mesh(vertices, faces)

        self._make_surface_layer(all_vertices,
                                 all_faces,
                                 name=f'{self.name} - particles',
                                 scale=self.datablock.pixel_size,
                                 # TODO: color
                                 )

    def make_volume_mesh(self):
        vertices, faces, _, _ = marching_cubes(self.volume.copy(), level=self.iso, step_size=self.step_size)  # need copy for readonly issues
        return vertices, faces

    def tile_mesh(self, vertices, faces):
        ori = self.datablock.orientations.data.values

        # find rotated mesh vertices for each particle
        all_vertices_rotated = (vertices @ ori)
        # then translate them to the right place and reshape to a normal list of coords
        pos = self.get_positions()
        all_vertices = (all_vertices_rotated + pos.data.reshape(-1, 1, 3)).reshape(-1, 3)

        # tile faces array but increment by len(vertices) every time
        incr = np.arange(len(pos)) * len(vertices)
        all_faces = faces.reshape(1, -1, 3) + incr.reshape(-1, 1, 1)
        all_faces = all_faces.reshape(-1, 3)
        return all_vertices, all_faces

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, volume):
        if volume.ndim != 3:
            raise ValueError(f'volumes must have ndim=3, got {volume.ndim}')
        if isinstance(volume, np.ndarray):
            volume = volume
        else:
            from ...datablocks import ImageBlock
            if isinstance(volume, ImageBlock):
                volume = volume.data
            elif isinstance(volume, xr.DataArray):
                volume = volume
            volume = volume.transpose('z', 'y', 'x').values
        self._volume = volume
