import pytest

from peepingtom.containers import DataCrate
from peepingtom.datablocks import PointBlock


def test_datacrate():
    dc = DataCrate()
    assert isinstance(dc, DataCrate)
    with pytest.raises(TypeError):
        dc.append(1)
    pb = PointBlock()
    dc.append(pb)
    assert len(dc) == 1
    dc += dc
    assert dc.data == [pb, pb]
