from collections import Counter

from ...core import ImageBlock, ParticleBlock

from ..utils import _path, listify
from .mrc import write_mrc
from .em import write_em
from .star import write_star


writers = {
    (ImageBlock,): (write_mrc, write_em,),
    (ParticleBlock,): (write_star,),
}


def get_writer(datablock):
    for dbtypes, writer_funcs in writers.items():
        if type(datablock) in dbtypes:
            # TODO: implement some logic
            return writer_funcs[0]
    raise ValueError(f'could not find a writer for {type(datablock)}')


def write(datablocks, paths, overwrite=False, strict=False, **kwargs):
    """
    wite a list of datablocks to disk
    """
    # sanitize input
    datablocks = listify(datablocks)
    paths = [_path(path) for path in listify(paths)]

    # check if numbers match
    if len(datablocks) != len(paths) and len(datablocks):
        # were we given a dir path?
        if len(paths) != 1:
            raise NotImplementedError
        elif any(path.is_file() for path in paths):
            raise ValueError(f'number of datablocks and paths must be equal; '
                             f'got {len(datablocks)} datablocks and {len(paths)} paths')
        else:
            # i guess it's a dir. convert it to paths
            # TODO: not great with a single datablock
            dir_path = paths[0]
            dir_path.mkdir(parents=True, exist_ok=True)
            paths = []
            count_same_name = Counter()
            for datablock in datablocks:
                count_same_name[datablock.name] += 1
                if idx := count_same_name[datablock.name] > 1:
                    path = dir_path / datablock.name + str(idx)
                else:
                    path = dir_path / datablock.name
                paths.append(path)


    for datablock, path in zip(datablocks, paths):
        if not overwrite and path.exists():
            raise ValueError('file {path} exists!')
        try:
            writer = get_writer(datablock)
            writer(datablock, path, overwrite=overwrite, **kwargs)
        except ValueError:
            if strict:
                raise
