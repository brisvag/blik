from ..datablock import DataBlock


class MultiBlock(DataBlock):
    """
    Unites multiple SimpleBlocks into a more complex data object

    Note: classes which inherit from 'MultiBlock' should call super().__init__()
    first in their constructors so that references to blocks are correctly defined.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._blocks = []

    def __setattr__(self, name, value):
        """
        Extend the functionality of __setattr__ to automatically add datablocks to the
        'blocks' attribute of a 'MultiBlock' when set
        """
        # excepting _parent is necessary here: self._parent is not supposed to be part of `blocks`
        if isinstance(value, DataBlock) and name != '_parent':
            self._blocks.append(value)
        super().__setattr__(name, value)

    @property
    def blocks(self):
        return self._blocks

    def depict(self, mode='default', **kwargs):
        super().depict(mode=mode, **kwargs)
        for block in self.blocks:
            block.depictors = self.depictors

    def __getitem__(self, key):
        subslices = []
        for block in self.blocks:
            subslices.append(block.__getitem__(key))
        return self.__view__(*subslices)

    def __len__(self):
        lengths = [len(block) for block in self.blocks]
        if all(ln == lengths[0] for ln in lengths):
            return len(self.blocks[0])
        raise TypeError(f"object of type '{type(self)}' has no len()")
