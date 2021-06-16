import numpy as np
from blik.datablocks.simpleblocks.imageblock import ImageBlock
from blik.depictors import ImageDepictor


def test_imageblock_instantiation():
    im = np.random.normal(0, 1, (28, 28, 28))
    block = ImageBlock(data=im)
    assert isinstance(block, ImageBlock)


def test_depiction():
    ib = ImageBlock(data=np.ones((10, 10, 10)))
    ib.init_depictor()
    assert isinstance(ib.depictors[0], ImageDepictor)
    ib.update()
