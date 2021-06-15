import numpy as np
from napari.layers import Shapes, Points

from blik.datablocks import LineBlock
from blik.depictors import LineDepictor


def test_line_depictor():
    lineblock = LineBlock(data=np.random.rand(5, 3))
    line_depictor = LineDepictor(lineblock)
    assert line_depictor.datablock is lineblock
    assert len(line_depictor.layers) == 0
    line_depictor.depict()
    assert len(line_depictor.layers) == 2
    assert isinstance(line_depictor.points, Points)
    assert isinstance(line_depictor.backbone, Shapes)
    line_depictor.update()
