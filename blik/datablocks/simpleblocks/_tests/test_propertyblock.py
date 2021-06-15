from blik.datablocks.simpleblocks.propertyblock import PropertyBlock


def test_propertyblock_instantiation():
    block = PropertyBlock(data={})
    assert isinstance(block, PropertyBlock)
