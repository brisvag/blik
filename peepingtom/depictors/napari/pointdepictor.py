from .blockdepictor import BlockDepictor


class PointDepictor(BlockDepictor):
    def depict(self):
        pkwargs = {'size': 3}

        self.make_points_layer(self.datablock.as_zyx(),
                               name=f'{self.name}',
                               **pkwargs)

    def changed(self):
        self.datablock.data = self.layers[0].data
