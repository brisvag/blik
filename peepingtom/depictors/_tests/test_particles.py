import numpy as np
from napari.layers import Vectors, Points

from peepingtom.core import ParticleBlock
from peepingtom.peeper import ParticleDepictor


def test_particle_depictor():
    particleblock = ParticleBlock(np.ones((2, 3)), np.ones((2, 3, 3)), {})
    particle_depictor = ParticleDepictor(particleblock, peeper=None)
    assert particle_depictor.datablock is particleblock
    particle_depictor.init_layers()
    assert len(particle_depictor.layers) == 2
    assert isinstance(particle_depictor.point_layer, Points)
    assert isinstance(particle_depictor.vector_layer, Vectors)
