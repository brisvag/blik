from .datablock import DataBlock
from .metamultiblock import MetaMultiBlock


class MultiBlock(DataBlock, metaclass=MetaMultiBlock):
    """
    Unites multiple SimpleBlocks into a more complex data object
    """
    _block_types = {}

    def __init__(self, **kwargs):
        self._blocks = []
        block_args = {k: {} for k in self._block_types.keys()}
        other_kwargs = {}
        for kwarg, value in kwargs.items():
            for block_name in block_args:
                if kwarg.startswith(f'{block_name}_'):
                    original_name = kwarg.replace(f'{block_name}_', '')
                    block_args[block_name][original_name] = value
                    break
            else:
                other_kwargs[kwarg] = value

        super().__init__(**other_kwargs)
        for block_name, block_type in self._block_types.items():
            block = block_type(**block_args[block_name], multiblock=self)
            self.__setattr__(block_name, block)
            self._blocks.append(block)

    @property
    def blocks(self):
        return self._blocks

    def depict(self, mode='default', **kwargs):
        super().init_depictor(mode=mode, **kwargs)
        for block in self.blocks:
            block.depictors = self.depictors

    def __getitem__(self, key):
        subslices = {}
        for block_name in self._block_types.keys():
            block = self.__getattribute__(block_name)
            sliced = block.__getitem__(key)
            subslices[f'{block_name}_data'] = sliced
        return self.__view__(**subslices)
