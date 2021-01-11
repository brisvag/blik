from .blockdepictor import BlockDepictor


class ImageDepictor(BlockDepictor):
    def depict(self):
        self.make_image_layer(self.datablock.data, name=f'{self.name} - image')
