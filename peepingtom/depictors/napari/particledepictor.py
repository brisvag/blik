import numpy as np
import xarray as xr

from .naparidepictor import NapariDepictor
from ...utils.colors import distinct_colors


class ParticleDepictor(NapariDepictor):
    def __init__(self, datablock):
        super().__init__(datablock)
        self.point_size = 2
        self.point_color = 'cornflowerblue'
        self.point_edge_color = 'black'
        self.vector_lengths = dict(z=10, y=5, x=5)
        self.vector_widths = dict(z=0.7, y=0.5, x=0.5)
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
                                scale=self.datablock.pixel_size,
                                properties=self.datablock.properties.data,
                                face_color=self.point_color,
                                size=self.point_size,
                                edge_color=self.point_edge_color,
                                )

        for ax, vectors in self.get_vectors().items():
            self._make_vectors_layer(vectors.values,  # need to use values cause napari complains
                                     name=f'{self.name} - particle orientations ({ax})',
                                     scale=self.datablock.pixel_size,
                                     edge_color=self.vector_colors[ax],
                                     length=self.vector_lengths[ax],
                                     edge_width=self.vector_widths[ax],
                                     )

    def get_positions(self):
        return self.datablock.positions.zyx * self.rescale

    def get_vectors(self):
        pos = self.get_positions()
        all_vectors = self.datablock.orientations.zyx_vectors()
        stacked = {}
        for ax, vectors in all_vectors.items():
            stacked[ax] = xr.concat([pos, vectors], 'v').transpose('n', 'v', 'spatial')
        return stacked

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
            self.points.data = pos.values  # workaround for xarray
            self.points.properties = self.datablock.properties.data

            vectors = self.get_vectors().values()
            for layer, vector in zip(self.vectors, vectors):
                layer.data = vector.values
