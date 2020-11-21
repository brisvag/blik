from .base import Depictor


class PointDepictor(Depictor):
    def init_layers(self, point_kwargs={}, vector_kwargs={}):
        pkwargs = {'size': 3}
        vkwargs = {'length': 10}

        pkwargs.update(point_kwargs)
        vkwargs.update(vector_kwargs)

        layer = self.make_points_layer(self.datablock.as_zyx(),
                                       name=f'{self.name}',
                                       **pkwargs)
        self.layers.append(layer)

    def push_changes(self):
        self.datablock.data = self.layers[0].data
