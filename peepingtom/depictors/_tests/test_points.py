import numpy as np
from napari.layers import Points

from peepingtom.core import PointBlock
from peepingtom.peeper import PointDepictor


def test_points_depictor():
    pointblock = PointBlock(np.ones((2, 3)))
    point_depictor = PointDepictor(pointblock, peeper=None)
    assert point_depictor.datablock is pointblock
    point_depictor.init_layers()
    assert len(point_depictor.layers) == 1
    assert isinstance(point_depictor.layers[0], Points)
