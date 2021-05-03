from pathlib import Path
from inspect import signature

from .peeper import Peeper
from .datablocks import DataBlock
from .utils import listify
from .io_ import read


def peep(obj, *args, **kwargs):
    """
    Generate a Peeper from an input object or by reading from paths.
    """
    if isinstance(obj, Peeper):
        return obj
    obj = listify(obj)
    if all(isinstance(el, DataBlock) for el in obj):
        return Peeper(obj, *args, **kwargs)
    if all(isinstance(el, (Path, str)) for el in obj):
        return read(obj, *args, **kwargs)
    raise ValueError(f'cannot peep type "{type(obj)}"')


read_sig = signature(read)
read_params = list(read_sig.parameters.values())
first_param = read_params.pop(0)
kwargs_param = read_params.pop()
read_params.insert(0, first_param.replace(name='obj'))

peeper_sig = signature(Peeper)
peeper_params = list(peeper_sig.parameters.values())
peeper_params.pop(0)

peep.__signature__ = read_sig.replace(parameters=(read_params + peeper_params + [kwargs_param]))
sep = '----------------------------------------------------------------'
peep.__doc__ = peep.__doc__ + sep + read.__doc__
