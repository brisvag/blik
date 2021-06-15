import numpy as np

from .naparidepictor import NapariDepictor
from ...utils import distinct_colors, dim_names_to_indexes


class ParticleDepictor(NapariDepictor):
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
        self.rescale = 1

    def depict(self, rescale=True):
        if rescale:
            self.set_rescale()

        pos = self.get_positions()
        self._make_points_layer(pos,
                                name=f'{self.name} - particle positions',
                                properties=self.datablock.properties.data,
                                face_color=self.point_color,
                                size=self.point_size,
                                edge_color=self.point_edge_color,
                                )

        for ax, vectors in self.get_vectors().items():
            self._make_vectors_layer(vectors,
                                     name=f'{self.name} - particle orientations ({ax})',
                                     edge_color=self.vector_colors[ax],
                                     length=self.vector_lengths[ax],
                                     edge_width=self.vector_widths[ax],
                                     )

    def get_positions(self):
        return self.datablock.positions.zyx * self.rescale * self.datablock.pixel_size

    def get_orientations_zyx(self):
        return self.datablock.orientations.data[:, ::-1, ::-1]

    def _unit_vector(self, axis):
        idx = dim_names_to_indexes(axis, order='zyx')[0]
        # initialise unit vector array
        unit_vector = np.zeros(self.datablock.ndim, dtype=float)
        unit_vector[idx] = 1
        return unit_vector

    def get_vectors(self):
        pos = self.get_positions()
        ori = self.get_orientations_zyx()
        axes = 'zyx'[-self.datablock.ndim:]
        all_vectors = {}
        for ax in axes:
            vectors = ori @ self._unit_vector(ax)
            shifted_vectors = np.stack([pos, vectors], axis=1)
            all_vectors[ax] = shifted_vectors
        return all_vectors

    def set_rescale(self):
        pos = self.datablock.positions.data
        if 0 <= pos.min().item() <= pos.max().item() <= 1:
            peeper = self.datablock.peeper
            if peeper:
                same_volume = peeper.volumes[self.datablock.volume]
                from ...datablocks import ImageBlock
                for db in same_volume:
                    if isinstance(db, ImageBlock):
                        self.rescale = db.shape
                        break

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
            self.points.data = pos
            self.points.properties = self.datablock.properties.data

            vectors = self.get_vectors().values()
            for layer, vector in zip(self.vectors, vectors):
                layer.data = vector
