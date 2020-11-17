import numpy as np
from napari.layers import Points

from ..base import Depictor


class PointDepictor(Depictor):
    def make_layers(self, point_kwargs={}, vector_kwargs={}):
        pkwargs = {'size': 3}
        vkwargs = {'length': 10}

        pkwargs.update(point_kwargs)
        vkwargs.update(vector_kwargs)

        layer = Points(self.datablock.zyx,
                       name=f'{self.name}',
                       **pkwargs)
        self.layers.append(layer)

    def push_changes(self):
        self.datablock.data = self.layers[0].data
