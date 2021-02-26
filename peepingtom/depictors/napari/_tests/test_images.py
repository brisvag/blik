import numpy as np
from napari.layers import Image

from peepingtom.datablocks import ImageBlock
from peepingtom.depictors import ImageDepictor


def test_image_depictor():
    imageblock = ImageBlock(np.ones((3, 3, 3)))
    image_depictor = ImageDepictor(imageblock)
    assert image_depictor.datablock is imageblock
    assert len(image_depictor.layers) == 1
    assert isinstance(image_depictor.layers[0], Image)
