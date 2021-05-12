from abc import ABCMeta
from inspect import signature, Parameter


class MetaBlock(ABCMeta):
    """
    Metaclass for datablocks. Provides programmatic init signature construction
    for all subclasses of DataBlock
    """
    def __new__(cls, name, bases, dct):
        new_cls = super().__new__(cls, name, bases, dct)

        super_params = []
        # bubble up all parameters to the top class
        for base in bases:
            base_sig = signature(base)
            params = list(base_sig.parameters.values())
            for param in params:
                if param.kind != Parameter.VAR_KEYWORD:
                    super_params.append(param)

        # get signature of this class
        self_sig = signature(new_cls.__init__)  # directly to init to avoid recursion issues
        self_params = list(self_sig.parameters.values())
        other_params = [p for p in super_params if p not in self_params]

        # merge and sort all params, and set new signature
        all_params = self_params + other_params
        all_params.sort(key=lambda x: x.kind)

        new_sig = self_sig.replace(parameters=(all_params))
        new_cls.__signature__ = new_sig
        return new_cls
