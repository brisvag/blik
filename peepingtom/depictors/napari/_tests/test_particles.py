import numpy as np
from napari.layers import Vectors, Points, Surface

from peepingtom.datablocks import ParticleBlock
from peepingtom.depictors import ParticlePointDepictor, ParticleMeshDepictor


def test_particle_point_depictor():
    particleblock = ParticleBlock(positions_data=np.ones((2, 3)),
                                  orientations_data=np.ones((2, 3, 3)),
                                  properties_data={'a': [1, 2]})
    particle_depictor = ParticlePointDepictor(particleblock)
    assert particle_depictor.datablock is particleblock
    assert len(particle_depictor.layers) == 0
    particle_depictor.depict()
    assert len(particle_depictor.layers) == 4
    assert isinstance(particle_depictor.points, Points)
    assert all(isinstance(vec, Vectors) for vec in particle_depictor.vectors)
    particle_depictor.update()
    particle_depictor.color_by_categorical_property('a')


def test_particle_mesh_depictor():
    particleblock = ParticleBlock(positions_data=np.ones((2, 3)),
                                  orientations_data=np.ones((2, 3, 3)),
                                  properties_data={'a': [1, 2]})
    volume = np.pad(np.ones((2, 2, 2)), 1)
    particle_depictor = ParticleMeshDepictor(particleblock, volume=volume)
    assert particle_depictor.datablock is particleblock
    assert len(particle_depictor.layers) == 0
    particle_depictor.depict()
    assert len(particle_depictor.layers) == 1
    assert isinstance(particle_depictor.layers[0], Surface)
