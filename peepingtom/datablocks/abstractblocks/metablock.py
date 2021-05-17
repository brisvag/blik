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

        # update the signature with unique and sorted parameters
        updated_cls = cls.update_signature(new_cls, super_params)
        return updated_cls

    @staticmethod
    def update_signature(cls, new_params):  # cls here is the new_cls
        # class signature (not equal to init signature if already changed!)
        prev_sig = signature(cls)
        prev_params = list(prev_sig.parameters.values())
        # init signature (if different from class signature)
        init_sig = signature(cls.__init__)
        init_params = list(init_sig.parameters.values())

        # merge and sort all params, and set new signature
        all_params = prev_params + init_params + new_params
        unique_params = []
        for param in all_params:
            if any(param.name == param_unique.name for param_unique in unique_params):
                continue
            unique_params.append(param)
        unique_params.sort(key=lambda x: x.kind)

        new_sig = prev_sig.replace(parameters=(unique_params))
        # if this fails because signature is non-writeable, uninstall pyside2.
        # for some reason, it makes all user-defined classes signatures unwriteable
        cls.__signature__ = new_sig
        return cls
