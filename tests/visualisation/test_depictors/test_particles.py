from napari.layers import Vectors, Points
from peepingtom.visualisation import ParticleDepictor

from ...test_data.blocks import particleblock


def test_particle_depictor():
    particle_depictor = ParticleDepictor(particleblock, peeper=None)
    assert particle_depictor.datablock is particleblock
    particle_depictor.make_layers()
    assert len(particle_depictor.layers) == 2
    assert isinstance(particle_depictor.point_layer, Points)
    assert isinstance(particle_depictor.vector_layer, Vectors)
