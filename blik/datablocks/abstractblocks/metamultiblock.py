from inspect import signature, Parameter

from .metablock import MetaBlock


class MetaMultiBlock(MetaBlock):
    """
    Metaclass for datablocks. Provides programmatic init signature construction
    for all subclasses of DataBlock
    """
    _inherited_params = ('name', 'volume', 'dataset', 'parent', 'view_of',
                         'pixel_size', 'dims_order')

    def __new__(cls, name, bases, dct):
        # update _block_types based on bases:
        if '_block_types' not in dct:
            dct['_block_types'] = {}
        block_types = dct['_block_types']
        for base in bases:
            base_block_types = base.__dict__.get('_block_types', {})
            block_types.update(base_block_types)

        new_cls = super().__new__(cls, name, bases, dct)

        renamed_params = []
        for block_name, block_type in block_types.items():
            block_sig = signature(block_type)
            params = list(block_sig.parameters.values())
            for param in params:
                if param.kind != Parameter.VAR_KEYWORD \
                        and param.name not in cls._inherited_params\
                        and param.name != 'self':
                    par_renamed = param.replace(name=f'{block_name}_{param.name}')
                    renamed_params.append(par_renamed)

        updated_cls = cls.update_signature(new_cls, renamed_params)
        return updated_cls
