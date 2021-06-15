import numpy as np
from napari.layers import Points

from blik.datablocks import PointBlock
from blik.depictors import PointDepictor


def test_points_depictor():
    pointblock = PointBlock(data=np.ones((2, 3)))
    point_depictor = PointDepictor(pointblock)
    assert point_depictor.datablock is pointblock
    assert len(point_depictor.layers) == 0
    point_depictor.depict()
    assert len(point_depictor.layers) == 1
    assert isinstance(point_depictor.layers[0], Points)
