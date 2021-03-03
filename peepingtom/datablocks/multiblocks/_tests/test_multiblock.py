from peepingtom.datablocks.multiblocks.multiblock import MultiBlock


def test_multiblock():
    block = MultiBlock()
    assert isinstance(block, MultiBlock)
