import numpy as np
from napari.layers import Vectors, Points

from peepingtom.datablocks import ParticleBlock
from peepingtom.depictors import ParticleDepictor


def test_particle_depictor():
    particleblock = ParticleBlock(positions_data=np.ones((2, 3)),
                                  orientations_data=np.ones((2, 3, 3)),
                                  properties_data={})
    particle_depictor = ParticleDepictor(particleblock)
    assert particle_depictor.datablock is particleblock
    assert len(particle_depictor.layers) == 0
    particle_depictor.depict()
    assert len(particle_depictor.layers) == 2
    assert isinstance(particle_depictor.points, Points)
    assert isinstance(particle_depictor.vectors, Vectors)
