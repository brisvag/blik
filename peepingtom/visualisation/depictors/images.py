from ..base import Depictor


class ImageDepictor(Depictor):
    def draw(self, image_kwargs={}, **kwargs):
        super().draw(**kwargs)

        ikwargs = {}
        ikwargs.update(image_kwargs)

        layer = self.viewer.add_image(self.datablock.data,
                                      name=f'{self.name} - image',
                                      **ikwargs)
        self.layers.append(layer)
