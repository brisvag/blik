from ..datablock import DataBlock
from ..simpleblocks import SimpleBlock
from ...utils import listify


class MultiBlock(DataBlock):
    """
    Unites multiple SimpleBlocks into a more complex data object

    Note: classes which inherit from 'MultiBlock' should call super().__init__()
    first in their constructors so that references to blocks are correctly defined
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._blocks = []

    def __setattr__(self, name, value):
        """
        Extend the functionality of __setattr__ to automatically add datablocks to the
        'blocks' attribute of a 'MultiBlock' when set
        """
        if isinstance(value, SimpleBlock):
            self._add_block(value)
        super().__setattr__(name, value)

    @property
    def blocks(self):
        return self._blocks

    @blocks.setter
    def blocks(self, blocks):
        blocks = listify(blocks)
        for block in blocks:
            if not isinstance(block, SimpleBlock):
                raise ValueError(f'MultiBlocks can only be made of SimpleBlocks, not "{type(block)}"')
        self._blocks = blocks

    def _add_block(self, block):
        """
        Adds a block to an existing list of SimpleBlocks in a MultiBlock

        This is particularly useful when extending the functionality of an existing
        MultiBlock object by inheritance
        """
        self._blocks.append(block)

    def __getitem__(self, key):
        subslices = []
        for block in self.blocks:
            subslices.append(block.__getitem__(key))
        return self.__newlike__(*subslices)

    def __len__(self):
        lengths = [len(block) for block in self.blocks]
        if all(l == lengths[0] for l in lengths):
            return len(self.blocks[0])
        raise TypeError(f"object of type '{type(self)}' has no len()")

    @staticmethod
    def _merge_data(multiblocks):
        blocks_data = []
        blocks_all = [mb.blocks for mb in multiblocks]
        # cryptic loop example: datablock types in "blocks" (a, b, c),
        # this loops through the list [(a1, a2, ...), (b1, b2, ...), (c1, c2, ...)]
        # so this separates the components of a list of multiblocks into a lists of
        # simple datablocks of the same type
        for blocks_by_type in zip(*blocks_all):
            blocks_data.append(blocks_by_type[0]._merge_data(blocks_by_type))
        return blocks_data

    @staticmethod
    def _stack_data(multiblocks):
        blocks_data = []
        blocks_all = [mb.blocks for mb in multiblocks]
        # cryptic loop example: datablock types in "blocks" (a, b, c),
        # this loops through the list [(a1, a2, ...), (b1, b2, ...), (c1, c2, ...)]
        # so this separates the components of a list of multiblocks into a lists of
        # simple datablocks of the same type
        for blocks_by_type in zip(*blocks_all):
            blocks_data.append(blocks_by_type[0]._stack_data(blocks_by_type))
        return blocks_data

    def _merge(self, multiblocks):
        return self.__newlike__(*self._merge_data(multiblocks))

    def _stack(self, multiblocks):
        return self.__newlike__(*self._stack_data(multiblocks))

    def _imerge(self, multiblocks):
        new_data = self._merge_data([self] + multiblocks)
        for block, data in zip(self.blocks, new_data):
            block.data = data

    def _istack(self, multiblocks):
        new_data = self._stack_data([self] + multiblocks)
        for block, data in zip(self.blocks, new_data):
            block.data = data
