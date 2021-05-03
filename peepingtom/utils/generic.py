from collections.abc import Iterable
from functools import wraps
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
    # "double decorator" is needed to have a decorator with additional arguments!
    # other_func / func are supposed to be different: other_func provides the signature,
    # func is the decorated function
    def inner_decorator(func):
        @wraps(other_func)
        def wrapper():
            func()
        sig = signature(other_func)
        params = list(sig.parameters.values())
        # discard first arguments
        for i in range(ignore_args + 1):
            params.pop(0)
        new_sig = sig.replace(parameters=(params))
        wrapper.__signature__ = new_sig
        return wrapper
    return inner_decorator
