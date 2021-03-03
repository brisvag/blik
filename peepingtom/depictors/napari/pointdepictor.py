from .naparidepictor import NapariDepictor


class PointDepictor(NapariDepictor):
    def depict(self):
        pkwargs = {'size': 3}

        self._make_points_layer(self.datablock.as_zyx(),
                               name=f'{self.name}',
                               **pkwargs)

    def changed(self, event):
        self.datablock.data = self.layers[0].data
