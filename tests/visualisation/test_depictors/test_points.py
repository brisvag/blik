from napari.layers import Points
from peepingtom.peeper import PointDepictor

from ...test_data.blocks import pointblock


def test_points_depictor():
    point_depictor = PointDepictor(pointblock, peeper=None)
    assert point_depictor.datablock is pointblock
    point_depictor.init_layers()
    assert len(point_depictor.layers) == 1
    assert isinstance(point_depictor.layers[0], Points)
