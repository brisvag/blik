import numpy as np

from peepingtom.datablocks.multiblocks.particleblock import ParticleBlock


def test_particleblock_instantiation():
    block = ParticleBlock(np.zeros((5, 3)), np.zeros((5, 3, 3)))
    assert isinstance(block, ParticleBlock)
