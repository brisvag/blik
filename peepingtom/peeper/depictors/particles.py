import numpy as np

from .base import Depictor


class ParticleDepictor(Depictor):
    def init_layers(self, point_kwargs={}, vector_kwargs={}):
        pkwargs = {'size': 3}
        vkwargs = {'length': 10}

        pkwargs.update(point_kwargs)
        vkwargs.update(vector_kwargs)

        p_layer = self.make_points_layer(self.datablock.positions.as_zyx(),
                                         name=f'{self.name} - particle positions',
                                         properties=self.datablock.properties.data,
                                         **pkwargs)
        self.layers.append(p_layer)

        # get positions and 'projection' vectors
        positions = self.datablock.positions.as_zyx()
        unit_z_rotated_order_xyz = self.datablock.orientations.oriented_vectors('z').reshape((-1, 3))
        unit_z_rotated_order_zyx = unit_z_rotated_order_xyz[:, ::-1]
        # attach appropriate higher dimensions indeces to vectors
        # TODO: make more general
        if self.datablock.positions.ndim > 3:
            padded = np.zeros_like(self.datablock.positions.data)
            padded[:, -3:] = unit_z_rotated_order_zyx
            unit_z_rotated_order_zyx = padded

        napari_vectors = np.stack([positions, unit_z_rotated_order_zyx], axis=1)
        v_layer = self.make_vectors_layer(napari_vectors,
                                          name=f'{self.name} - particle orientations',
                                          **vkwargs)
        self.layers.append(v_layer)

    @property
    def point_layer(self):
        return self.layers[0]

    @property
    def vector_layer(self):
        return self.layers[1]

    def update(self):
        try:
            self.point_layer.properties = {k: v for k, v in self.datablock.properties.data.items()
                                           if len(v) == len(self.datablock.positions.data)}
        except KeyError:
            # happens if layers do not exist: just pass
            pass
