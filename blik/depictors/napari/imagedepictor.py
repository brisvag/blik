from .naparidepictor import NapariDepictor


class ImageDepictor(NapariDepictor):
    def depict(self):
        self._make_image_layer(self.datablock.data,
                               name=f'{self.name} - image',
                               scale=self.datablock.pixel_size)
