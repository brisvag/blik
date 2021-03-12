from pathlib import Path

from .peeper import Peeper
from .datablocks import DataBlock
from .utils import listify
from .io_ import read


def peep(obj, *args, **kwargs):
    if isinstance(obj, Peeper):
        return obj
    obj = listify(obj)
    if all(isinstance(el, DataBlock) for el in obj):
        return Peeper(obj, *args, **kwargs)
    if all(isinstance(el, (Path, str)) for el in obj):
        return read(obj, *args, **kwargs)
    raise ValueError(f'cannot peep type "{type(obj)}"')
