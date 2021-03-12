import re
from collections import defaultdict
from itertools import zip_longest

from ..utils import _path, ParseError
from ...utils import listify
from .star import read_star
from .mrc import read_mrc
from .em import read_em
from .tbl import read_tbl

from ...peeper import Peeper


# a mapping of file extensions to readers, tuple map to tuples:
#   - multiple extensions values in the keys use the same readers
#   - multiple readers are called in order from highest to lowers in case previous ones fail
# TODO: put this directly in the readers to make it plug and play?
readers = {
    ('.star',): (read_star,),
    ('.mrc', '.mrcs', '.map'): (read_mrc,),
    ('.em',): (read_em,),
    ('.tbl'): (read_tbl,),
}


def read_file(file_path, **kwargs):
    """
    read a single file with the appropriate parser and return a list of datablocks
    """
    for ext, funcs in readers.items():
        if file_path.suffix in ext:
            for func in funcs:
                try:
                    datablocks = listify(func(file_path, **kwargs))
                    return datablocks
                except ParseError:
                    # this will be raised by individual readers when the file can't be read.
                    # Keep trying until all options are exhausted
                    continue
    raise ParseError(f'could not read {file_path}')


def find_files(paths, filters=None, recursive=False, max=None):
    """
    take a path or iterable thereof and find all the contained readable files
    filters: a regex-like strings or iterable thereof used to match filenames
    max: max number of files to read
    """
    # sanitize input
    paths = listify(paths)
    paths = [_path(path) for path in paths]
    filters = listify(filters)

    # extract files
    files = []
    for path in paths:
        if not path.exists():
            raise FileNotFoundError(f'{path} does not exist')

        # find all the readable files, if any
        if path.is_file():
            files.append(path)
        elif path.is_dir():
            basedir = '.'
            if recursive:
                basedir = '**'
            known_formats = [ext for formats in readers for ext in formats]
            for ext in known_formats:
                files.extend(file for file in path.glob(f'{basedir}/*{ext}'))
        if not files:
            raise FileNotFoundError(f'{path} does not contain any files of a know type')

    # filter files if requested
    files = [file for file in files if all(re.search(regex, str(file)) for regex in filters)]

    if max is None:
        max = len(files) + 1
    return files[:max]


def read(paths,
         filters=None,
         name_regex=None,
         mode=None,
         recursive=False,
         strict=False,
         max=None,
         **kwargs):
    r"""
    read generic path(s) and construct a peeper accordingly

    filters: a regex string or iterable thereof used to select filenames [default: '.*']
    name_regex: a regex used to infer DataBlock names from paths. For example:
                'Protein_\d+' will match 'MyProtein_10.star' and 'MyProtein_001.mrc'
                and name the respective DataBlocks 'Protein_10' and 'Protein_01'
    mode: how to arrange DataBlocks into volumes
        - lone: each datablock in a separate volume
        - zip_by_type: one of each datablock type per volume
        - bunch: all datablocks in a single volume
    recursive: navigate directories recursively to find files
    strict: if set to true, immediately fail if a matched filename cannot be read by PeepingTom
    max: max number of files to read
    """
    # if changing the signature of this function, change the one in `__main__.cli` as well!
    modes = ('lone', 'zip_by_type', 'bunch')

    if mode is not None and mode not in modes:
        raise ValueError(f'mode can only be one of {modes}')

    datablocks = []
    for file in find_files(paths, filters=filters, recursive=recursive, max=max):
        try:
            datablocks.extend(read_file(file, name_regex=name_regex, **kwargs))
        except ParseError:
            if strict:
                raise
    if not datablocks:
        raise ParseError(f'could not read any data from {paths}')

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
        for lst in datablocks_by_type.values():
            lst.sort()
        for dbs in zip_longest(*datablocks_by_type.values()):
            for db in dbs:
                db.volume = dbs[0].name
        # TODO: add rescaling?

    return Peeper(datablocks)
