from collections.abc import Iterable
from pathlib import Path


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
