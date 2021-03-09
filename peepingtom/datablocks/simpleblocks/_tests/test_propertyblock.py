from peepingtom.datablocks.simpleblocks.propertyblock import PropertyBlock


def test_propertyblock_instantiation():
    block = PropertyBlock({})
    assert isinstance(block, PropertyBlock)
