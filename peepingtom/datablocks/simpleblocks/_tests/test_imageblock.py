import numpy as np
from peepingtom.datablocks.simpleblocks.imageblock import ImageBlock
from peepingtom.depictors import ImageDepictor


def test_imageblock_instantiation():
    im = np.random.normal(0, 1, (28, 28, 28))
    block = ImageBlock(im)
    assert isinstance(block, ImageBlock)


def test_depiction():
    ib = ImageBlock(np.zeros((3, 3, 3)))
    ib.depict()
    assert isinstance(ib.depictors[0], ImageDepictor)
    ib.update()
