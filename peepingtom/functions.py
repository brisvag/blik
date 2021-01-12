from collections.abc import Iterable
from pathlib import Path

from .containers import DataSet, DataCrate
from .datablocks import DataBlock
from .utils import listify
from .io_ import read


def merge(datablocks):
    """
    merges a list of datablocks into a single datablock
    """
    cls = type(datablocks[0])
    if not all(isinstance(db, cls) for db in datablocks):
        raise TypeError('cannot merge datablocks of different types')
    return datablocks[0]._merge(datablocks)


def stack(datablocks):
    """
    stacks a list of datablocks into a single datablock
    """
    cls = type(datablocks[0])
    if not all(isinstance(db, cls) for db in datablocks):
        raise TypeError('cannot stack datablocks of different types')
    return datablocks[0]._stack(datablocks)


def peep(obj, *args, **kwargs):
    if isinstance(obj, DataSet):
        return obj
    obj = listify(obj)
    if all(isinstance(el, DataCrate) for el in obj):
        return DataSet(obj)
    if all(isinstance(el, DataBlock) for el in obj):
        return DataSet([DataCrate(db) for db in obj])
    if all(isinstance(el, (Path, str)) for el in obj):
        return read(obj)
    raise ValueError(f'cannot peep type "{type(obj)}"')
