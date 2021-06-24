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
        self._rescale = 1

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

    def _pad_to_ndim(self, array, fill_value):
        """
        pad an array containing only spatial dimensions to match the total amount of dimensions
        of the particles (including non-spatial ones)

        fill_value: value used to fill the padding
        """
        non_spatial_dims = max(self.datablock.positions.data.shape[1] - 3, 0)
        if array.ndim == 1:
            # 1D array, pad to the left
            return np.pad(array, (non_spatial_dims, 0), constant_values=fill_value)
        elif array.ndim == 2:
            # 2D array, pad to the left of 2nd dim
            return np.pad(array, ((0, 0), (non_spatial_dims, 0)), constant_values=fill_value)
        raise ValueError(f"cannot pad array of shape {array.shape}")

    def get_positions(self):
        positions = self.datablock.positions.as_zyx
        # padding must be done with ones to be neutral in multiplication
        padded_pixel_size = self._pad_to_ndim(self.datablock.pixel_size, 1)
        padded_rescale = self._pad_to_ndim(self.rescale, 1)
        return positions * padded_rescale * padded_pixel_size

    def _unit_vector(self, axis):
        idx = dim_names_to_indexes(axis, order='zyx')[0]
        # initialise unit vector array
        unit_vector = np.zeros(3, dtype=float)
        unit_vector[idx] = 1
        return unit_vector

    def get_vectors(self):
        pos = self.get_positions()
        ori = self.datablock.orientations.as_zyx
        all_vectors = {}
        for ax in 'zyx':
            vectors = ori @ self._unit_vector(ax)
            # must pad to match positions (with eros, otherwise vectors will pierce non-spatial dims)
            shifted_vectors = np.stack([pos, self._pad_to_ndim(vectors, 0)], axis=1)
            all_vectors[ax] = shifted_vectors
        return all_vectors

    def set_rescale(self):
        """
        dig through all the datablocks sharing this volume. If any are images, use their shape
        to rescale the normalized coords of the particles to the original ones
        """
        if self.datablock.volume is None:
            # None volumes are by definition single datablocks so we can should skip them
            return
        pos = self.datablock.positions.data
        if 0 <= pos.min().item() <= pos.max().item() <= 1:
            datasets = self.datablock.datasets
            for dataset in datasets:
                same_volume = dataset.volumes[self.datablock.volume]
                from ...datablocks import ImageBlock
                for db in same_volume:
                    if isinstance(db, ImageBlock):
                        self._rescale = db.shape
                        break

    @property
    def rescale(self):
        return np.broadcast_to(self._rescale, (3,))

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
