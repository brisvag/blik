from peepingtom.peeper import Peeper
from peepingtom.datablocks import PointBlock

p = Peeper(PointBlock())


def test_show():
    p.show()
