import numpy as np

from peepingtom.datablocks.multiblocks.particleblock import ParticleBlock


def test_particleblock_instantiation():
    block = ParticleBlock(positions_data=np.zeros((5, 3)), orientations_data=np.zeros((5, 3, 3)), properties_data={})
    assert isinstance(block, ParticleBlock)
