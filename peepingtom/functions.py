from pathlib import Path

from .peeper import Peeper
from .datablocks import DataBlock
from .utils import listify, inherit_signature
from .io_ import read


def which_isinstance(iterable, type):
    """
    filter an iterable and return only elements of a specific type
    """
    ret = []
    for item in iterable:
        if isinstance(item, type):
            ret.append(item)
    return ret


@inherit_signature(read, Peeper, ignore_args=['globs', 'name', 'datablocks'], add_args={'name': None})
def peep(*args, **kwargs):
    """
    Generate a Peeper from an input object or by reading from paths.
    Additionally to all the arguments of `read`, this accepts Peepers and DataBlocks
    """
    datablocks = []
    globs = []
    for obj in args:
        obj = listify(obj)
        for item in obj:
            if isinstance(item, Peeper):
                datablocks.extend(item.datablocks)
            elif isinstance(item, DataBlock):
                datablocks.append(item)
            elif isinstance(item, (Path, str)):
                globs.append(item)
            else:
                raise ValueError(f'cannot peep type "{type(obj)}"')
    peeper = read(*globs, **kwargs)
    peeper.extend(datablocks)
    return peeper
