from pathlib import Path

from .dataset import DataSet
from .datablocks import DataBlock
from .utils import listify, inherit_signature
from .io_ import read


@inherit_signature(read, DataSet, ignore_args=['globs', 'name', 'datablocks'], add_args={'name': None})
def peep(*args, **kwargs):
    """
    Generate a DataSet from an input object or by reading from paths.
    Additionally to all the arguments of `read`, this accepts DataSets and DataBlocks
    """
    datablocks = []
    globs = []
    for obj in args:
        obj_list = listify(obj)
        for item in obj_list:
            if isinstance(item, DataBlock):
                datablocks.append(item)
            elif isinstance(item, (Path, str)):
                globs.append(item)
            else:
                raise ValueError(f'cannot peep type "{type(obj)}"')
    dataset = read(*globs, **kwargs)
    dataset.extend(datablocks)
    return dataset
