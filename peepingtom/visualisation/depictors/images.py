from napari.layers import Image

from ..base import Depictor


class ImageDepictor(Depictor):
    def init_layers(self, image_kwargs={}, **kwargs):
        ikwargs = {}
        ikwargs.update(image_kwargs)

        layer = Image(self.datablock.data,
                      name=f'{self.name} - image',
                      **ikwargs)
        self.layers.append(layer)
