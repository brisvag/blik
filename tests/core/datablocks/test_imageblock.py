import numpy as np
from peepingtom.core.datablocks import ImageBlock


def test_imageblock_instantiation():
    im = np.random.normal(0, 1, (28, 28, 28))
    block = ImageBlock(im)
    assert isinstance(block, ImageBlock)
