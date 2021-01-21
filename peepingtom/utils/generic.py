from collections.abc import Iterable
from pathlib import Path
from inspect import signature

from .dispatchlist import DispatchList


def listify(obj):
    """
    transform input into an appropriate list, unless already list-like
    """
    # avoid circular import
    from ..datablocks import DataBlock
    if isinstance(obj, Iterable) and not isinstance(obj, (str, DispatchList, DataBlock, Path)):
        return list(obj)
    if obj is None:
        return []
    return [obj]



def wrapper_method(other_func, ignore_args=0):
    """
    method decorator that copies a function's signature and docstring onto the method
    removes and ignores the first n arguments
    """
    def wrapper(func):
        func.__doc__ = other_func.__doc__
        sig = signature(other_func)
        params = list(sig.parameters.values())
        # discard first arguments
        new_sig = sig.replace(parameters=params[ignore_args + 1:])
        func.__signature__ = new_sig
        return func
    return wrapper
