from napari.layers import Shapes, Points
from peepingtom.visualisation import LineDepictor

from ...test_data.blocks import lineblock


def test_line_depictor():
    line_depictor = LineDepictor(lineblock, peeper=None)
    assert line_depictor.datablock is lineblock
    line_depictor.make_layers()
    assert len(line_depictor.layers) == 2
    assert isinstance(line_depictor.points_layer, Points)
    assert isinstance(line_depictor.backbone_layer, Shapes)
