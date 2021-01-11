import numpy as np
from napari.layers import Image

from peepingtom.core import ImageBlock
from peepingtom.peeper import ImageDepictor


def test_image_depictor():
    imageblock = ImageBlock(np.ones((3, 3, 3)))
    image_depictor = ImageDepictor(imageblock, peeper=None)
    assert image_depictor.datablock is imageblock
    image_depictor.init_layers()
    assert len(image_depictor.layers) == 1
    assert isinstance(image_depictor.layers[0], Image)
