from peepingtom.datablocks import PointBlock, LineBlock, ParticleBlock
from peepingtom.peeper import Peeper
from peepingtom.alchemists import PointToLineAlchemist, PointToParticleAlchemist


pb = PointBlock(data=[[0, 0], [1, 1], [2, 2], [3, 3]], ndim=2)
p = Peeper(pb)


def test_point_to_line():
    p2l = PointToLineAlchemist(pb)
    assert isinstance(p2l.outputs[0], LineBlock)
    assert p2l.outputs[0].data is pb.data
    p2l.update()


def test_point_to_particle():
    p2p = PointToParticleAlchemist(pb)
    assert isinstance(p2p.outputs[0], ParticleBlock)
    assert p2p.outputs[0].positions.data is pb.data
    p2p.update()
