from collections import defaultdict
from itertools import zip_longest
from pathlib import Path
import logging

from .star import read_star
from .mrc import read_mrc
from .em import read_em
from .tbl import read_tbl
from .box import read_box
from .cbox import read_cbox

from ..utils import ParseError

from ...dataset import DataSet
from ...datablocks import DataBlock
from ...utils import listify, inherit_signature


logger = logging.getLogger(__name__)

# a mapping of file extensions to readers, tuple map to tuples (don't forget trailing comma!):
#   - multiple extensions values in the keys use the same readers
#   - multiple readers are called in order from highest to lowers in case previous ones fail
# TODO: put this directly in the readers to make it plug and play?
readers = {
    ('.star',): (read_star,),
    ('.mrc', '.mrcs', '.map'): (read_mrc,),
    ('.em',): (read_em,),
    ('.tbl',): (read_tbl,),
    ('.box',): (read_box,),
    ('.cbox',): (read_cbox,),
}

known_formats = [ext for formats in readers for ext in formats]


def read_file(file_path, **kwargs):
    """
    read a single file with the appropriate parser and return a list of datablocks
    """
    for ext, funcs in readers.items():
        if file_path.suffix in ext:
            for func in funcs:
                try:
                    datablocks = listify(func(file_path, **kwargs))
                    for db in datablocks:
                        db.file_path = file_path
                    return datablocks
                except ParseError:
                    # this will be raised by individual readers when the file can't be read.
                    # Keep trying until all options are exhausted
                    continue
    raise ParseError(f'could not read {file_path}')


def root_relative_glob(glob):
    return str(Path(glob).expanduser().resolve().relative_to('/'))


def expand_globs(globs):
    """
    expand globs to single files
    """
    globs = listify(globs)
    for glob in globs:
        glob = root_relative_glob(glob)
        yield from Path('/').glob(glob)


def filter_readable(paths):
    for path in paths:
        if path.is_file() and path.suffix in known_formats:
            yield path


def find_files(globs):
    """
    take a glob pattern or iterable thereof and find all readable files that match it
    """
    files = expand_globs(globs)
    readable = filter_readable(files)

    yield from readable


def read_files(*globs,
         name='DataSet',
         mode=None,
         name_regex=None,
         pixel_size=None,
         strict=False,
         lazy=True,
         **kwargs):
    r"""
    Read any number of paths or glob patterns and construct a DataSet accordingly.

    DataSet and Datablock construction arguments:
        name: the name of the DataSet (default: DataSet)
        mode: how to arrange DataBlocks into volumes. By default tries to guess.
            - lone: each datablock in a separate volume
            - zip_by_type: one of each datablock type per volume
            - bunch: all datablocks in a single volume
        name_regex: a regex used to infer DataBlock names from paths. For example:
                    'Protein_\d+' will match 'MyProtein_10.star' and 'MyProtein_001.mrc'
                    and name the respective DataBlocks 'Protein_10' and 'Protein_01'
        pixel_size: manually set the pixel size (overrides the one read from file)
    File reading arguments:
        strict: if set to true, immediately fail if a matched filename cannot be read by Blik
    Performance arguments:
        lazy: read data lazily (if possible)
    """
    # if changing the signature of this function, change the one in `__main__.cli` as well!
    modes = ('lone', 'zip_by_type', 'bunch')

    if mode is not None and mode not in modes:
        raise ValueError(f'mode can only be one of {modes}')

    datablocks = []
    for file in find_files(globs):
        try:
            logger.info(f'attempting to read "{file}"')
            datablocks.extend(read_file(file, name_regex=name_regex, pixel_size=pixel_size,
                                        lazy=lazy, **kwargs))
        except ParseError as e:
            logger.info(f'failed to read "{file}": {e}')
            if strict:
                raise
    if not datablocks and strict:
        raise ParseError(f'could not read any data from {globs}')

    datablocks_by_type = defaultdict(list)
    for db in datablocks:
        datablocks_by_type[type(db)].append(db)

    if mode is None:
        # check if there are multiple types and lengths are all the same
        if len(datablocks_by_type) > 1:
            count_per_type = [len(db_type) for db_type in datablocks_by_type.values()]
            if len(set(count_per_type)) == 1:
                mode = 'zip_by_type'
            else:
                mode = 'lone'
        else:
            mode = 'lone'

    if mode == 'lone':
        for db in datablocks:
            db.volume = db.name
    elif mode == 'bunch':
        pass
    elif mode == 'zip_by_type':
        # TODO: this is quite finnicky. We need a smarter way of handling volumes
        for lst in datablocks_by_type.values():
            lst.sort()
        for dbs in zip_longest(*datablocks_by_type.values()):
            for db in dbs:
                db.volume = dbs[0].name

    return DataSet(datablocks, name=name)


@inherit_signature(read_files, DataSet, ignore_args=['name', 'datablocks', 'view_of'], add_args={'name': None})
def read(*args, **kwargs):
    """
    Generate a DataSet from an input object or by reading from paths.
    Additionally to all the arguments of `read_files`, this accepts DataSets and DataBlocks
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
                raise ValueError(f'cannot read type "{type(obj)}"')
    dataset = read_files(*globs, **kwargs)
    dataset.extend(datablocks)
    return dataset
