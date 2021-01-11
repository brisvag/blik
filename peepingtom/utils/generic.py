from collections.abc import Iterable
from pathlib import Path
from inspect import signature


def listify(obj):
    """
    transform input into an appropriate list, unless already list-like
    """
    # avoid circular import
    from ..core import DispatchList, DataBlock
    if isinstance(obj, Iterable) and not isinstance(obj, (str, DispatchList, DataBlock, Path)):
        return list(obj)
    if obj is None:
        return []
    return [obj]



def wrapper_method(other_func):
    """
    method decorator that copies a function's signature and docstring onto the method
    removes and ignores the first positional argument (assumed to change from function to method form)
    """
    def wrapper(func):
        func.__doc__ = other_func.__doc__
        sig = signature(other_func)
        params = iter(sig.parameters.items())
        # discard first argument
        next(params)
        new_sig = sig.replace(parameters=dict(params))
        func.__signature__ = new_sig
        return func
    return wrapper
