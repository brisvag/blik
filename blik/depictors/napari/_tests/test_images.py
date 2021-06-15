import numpy as np
from napari.layers import Image

from blik.datablocks import ImageBlock
from blik.depictors import ImageDepictor


def test_image_depictor():
    imageblock = ImageBlock(data=np.ones((10, 10, 10)))
    image_depictor = ImageDepictor(imageblock)
    assert image_depictor.datablock is imageblock
    assert len(image_depictor.layers) == 0
    image_depictor.depict()
    assert len(image_depictor.layers) == 1
    assert isinstance(image_depictor.layers[0], Image)
