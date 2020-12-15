import numpy as np
from napari.layers import Shapes, Points

from peepingtom.core import LineBlock
from peepingtom.peeper import LineDepictor


def test_line_depictor():
    lineblock = LineBlock(np.random.rand(5, 3))
    line_depictor = LineDepictor(lineblock, peeper=None)
    assert line_depictor.datablock is lineblock
    line_depictor.init_layers()
    assert len(line_depictor.layers) == 2
    assert isinstance(line_depictor.points_layer, Points)
    assert isinstance(line_depictor.backbone_layer, Shapes)
