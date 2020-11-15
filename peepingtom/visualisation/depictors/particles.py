import numpy as np

from ..base import Depictor


class ParticleDepictor(Depictor):
    def draw(self, point_kwargs={}, vector_kwargs={}, **kwargs):
        super().draw(**kwargs)

        pkwargs = {'size': 3}
        vkwargs = {'length': 10}

        pkwargs.update(point_kwargs)
        vkwargs.update(vector_kwargs)

        p_layer = self.viewer.add_points(self.datablock.positions.zyx,
                                         name=f'{self.name} - particle positions',
                                         properties=self.datablock.properties.data,
                                         **pkwargs)
        self.layers.append(p_layer)

        # get positions and 'projection' vectors
        positions = self.datablock.positions.zyx
        unit_z_rotated_order_xyz = self.datablock.orientations.oriented_vectors('z').reshape((-1, 3))
        unit_z_rotated_order_zyx = unit_z_rotated_order_xyz[:, ::-1]

        napari_vectors = np.stack([positions,
                                   unit_z_rotated_order_zyx],
                                  axis=1)
        v_layer = self.viewer.add_vectors(napari_vectors,
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