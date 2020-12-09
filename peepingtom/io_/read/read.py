from ..utils import _path
from .star import read_star
from .mrc import read_mrc

# a mapping of file extensions to readers, tuple map to tuples:
#   - multiple extensions values in the keys use the same readers
#   - multiple readers are called in order from highest to lowers in case previous ones fail
readers = {
    ('.star',): (read_star,),
    ('.mrc',): (read_mrc,),
}


def read_file(file_path, **kwargs):
    """
    read a single file and return a list of datablocks
    """
    for ext, funcs in readers.items():
        if file_path.suffix in ext:
            for func in funcs:
                try:
                    datablocks = func(file_path, **kwargs)
                    # simplify higher level reading
                    if not isinstance(datablocks, list):
                        datablocks = [datablocks]
                    return datablocks
                except ValueError:
                    # this will be raised by individual readers when the file can't be read.
                    # Keep trying until all options are exhausted
                    continue
    raise ValueError(f'could not read {file_path}')


def read(path, recursive=False, strict=False, **kwargs):
    """
    read a generic path into the appropriate datablocks
    strict: if set to False, ignore failures and read what possible
    """
    path = _path(path)
    if not path.exists():
        raise FileNotFoundError(f'{path} does not exist')

    # find all the readable files, if any
    files = []
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

    datablocks = []
    for file in files:
        print(file)
        try:
            dbs = read_file(file, **kwargs)
            print(dbs)
            if not isinstance(dbs, list):
                dbs = [dbs]
            datablocks.extend(dbs)
        except ValueError:
            if strict:
                raise
    if not datablocks:
        raise ValueError(f'could not read any data from {path}')
    return datablocks
