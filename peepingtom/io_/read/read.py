import re
from collections import defaultdict
from itertools import zip_longest

from ..utils import _path, listify
from .star import read_star
from .mrc import read_mrc
from .em import read_em

from ...core import DataCrate
from ...utils import AttributedList


# a mapping of file extensions to readers, tuple map to tuples:
#   - multiple extensions values in the keys use the same readers
#   - multiple readers are called in order from highest to lowers in case previous ones fail
# TODO: put this directly in the readers to make it plug and play?
readers = {
    ('.star',): (read_star,),
    ('.mrc',): (read_mrc,),
    ('.em',): (read_em,),
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
                except ValueError:
                    # this will be raised by individual readers when the file can't be read.
                    # Keep trying until all options are exhausted
                    continue
    raise ValueError(f'could not read {file_path}')


def find_files(paths, filters=None, recursive=False):
    """
    take a path or iterable thereof and find all the contained readable files
    filters: a regex-like strings or iterable thereof used to match filenames
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

    return files


def read_to_datablocks(paths, filters=None, recursive=False, strict=False, **kwargs):
    """
    read generic path(s) into the appropriate datablocks
    strict: if set to False, ignore failures and read what possible
    """
    datablocks = []
    for file in find_files(paths, filters=filters, recursive=recursive):
        try:
            datablocks.extend(read_file(file, **kwargs))
        except ValueError:
            if strict:
                raise
    if not datablocks:
        raise ValueError(f'could not read any data from {paths}')
    return datablocks


def read(paths, mode=None, **kwargs):
    """
    read generic path(s) and construct datacrates accordingly
    mode:
        - lone: each datablock in a separate crate
        - zip_by_type: crates with one of each datablock type
        - bunch: all datablocks in a single crate
    """
    modes = ('lone', 'zip_by_type', 'bunch')

    if mode is not None and mode not in modes:
        raise ValueError(f'mode can only be one of {modes}')

    datablocks = read_to_datablocks(paths, **kwargs)
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
        crates = [DataCrate(db) for db in datablocks]
    elif mode == 'bunch':
        crates = [DataCrate(datablocks)]
    elif mode == 'zip_by_type':
        crates = []
        for dbs in zip_longest(datablocks_by_type.values()):
            crates.append(DataCrate(dbs))
        # TODO: add rescaling?

    return AttributedList(crates)
