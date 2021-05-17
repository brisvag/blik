from collections.abc import Iterable
from pathlib import Path
from functools import wraps
import inspect


def listify(obj):
    """
    transform input into an appropriate list, unless already list-like
    """
    # avoid circular import
    from ..datablocks import DataBlock
    if isinstance(obj, Iterable):
        if isinstance(obj, (str, DataBlock, Path)):
            return [obj]
        else:
            return list(obj)
    if obj is None:
        return []
    return [obj]


def inherit_signature(*other_functions, ignore_args=None, add_args={}):
    """
    meta-decorator that copies functions' signature and docstrings onto another,
    ignoring arguments as requested and patching docstrings together
    """
    ignore_args = listify(ignore_args)

    # "double decorator" is needed to have a decorator with additional arguments!
    # other_functions / func are supposed to be different: other_functions provide the signature,
    # func is the decorated function
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        all_params = []
        for other_func in other_functions:
            sig = inspect.signature(other_func)
            params = list(sig.parameters.values())
            # discard arguments
            keep_params = []
            for par in params:
                if par.name not in ignore_args:
                    keep_params.append(par)
            all_params.extend(keep_params)

        for par_name, default in add_args.items():
            par = inspect.Parameter(name=par_name, default=default, kind=inspect.Parameter.KEYWORD_ONLY)
            all_params.append(par)

        sorted_params = sorted(all_params, key=lambda x: x.kind)
        new_sig = sig.replace(parameters=(sorted_params))
        wrapper.__signature__ = new_sig

        sep = '-' * 80
        funcs = [func] + list(other_functions)
        docstr = sep.join([f.__doc__ for f in funcs if f.__doc__ is not None])
        wrapper.__doc__ = docstr

        return wrapper
    return decorator
