from .base import Depictor


class ImageDepictor(Depictor):
    def init_layers(self, image_kwargs={}, **kwargs):
        ikwargs = {}
        ikwargs.update(image_kwargs)

        layer = self.make_image_layer(self.datablock.data,
                                      name=f'{self.name} - image',
                                      **ikwargs)
        self.layers.append(layer)
