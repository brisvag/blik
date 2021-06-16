import numpy as np
from napari.layers import Vectors, Points

from blik.datablocks import ParticleBlock
from blik.depictors import ParticleDepictor


def test_particle_depictor():
    particleblock = ParticleBlock(positions_data=np.ones((2, 3)),
                                  orientations_data=np.ones((2, 3, 3)),
                                  properties_data={'a': [1, 2]})
    particle_depictor = ParticleDepictor(particleblock)
    assert particle_depictor.datablock is particleblock
    assert len(particle_depictor.layers) == 0
    particle_depictor.depict()
    assert len(particle_depictor.layers) == 4
    assert isinstance(particle_depictor.points, Points)
    assert all(isinstance(vec, Vectors) for vec in particle_depictor.vectors)
    particle_depictor.update()
    particle_depictor.color_by_categorical_property('a')
