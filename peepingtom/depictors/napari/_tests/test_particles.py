import numpy as np
from napari.layers import Vectors, Points

from peepingtom.datablocks import ParticleBlock
from peepingtom.depictors import ParticleDepictor


def test_particle_depictor():
    particleblock = ParticleBlock(np.ones((2, 3)), np.ones((2, 3, 3)), {})
    particle_depictor = ParticleDepictor(particleblock)
    assert particle_depictor.datablock is particleblock
    assert len(particle_depictor.layers) == 2
    assert isinstance(particle_depictor.points, Points)
    assert isinstance(particle_depictor.vectors, Vectors)
