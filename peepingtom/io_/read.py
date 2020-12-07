from .utils import _path, known_filetypes
from .crates import star_to_crates, mrc_to_crates, zip_mrc_star_to_crates


def find_files(path, recursive=False):
    path = _path(path)

    if not path.exists():
        raise FileNotFoundError(f'{path} does not exist')

    files = []
    if path.is_file():
        if path.suffix in known_filetypes:
            files.append(path)
        else:
            raise ValueError(f'{path} is not a known file type')

    elif path.is_dir():
        basedir = '.'
        if recursive:
            basedir = '**'
        for ext in known_filetypes:
            for file_path in path.glob(f'{basedir}/*{ext}'):
                files.append(file_path)
        if not files:
            raise FileNotFoundError(f'{path} does not contain any files of a know type')

    return files


# READERS

def mrc_reader(paths_by_ext):
    return mrc_to_crates(paths_by_ext['.mrc'])


def star_reader(paths_by_ext):
    return star_to_crates(paths_by_ext['.star'])


def zip_mrc_star_reader(paths_by_ext):
    mrc_files = paths_by_ext['.mrc']
    star_files = paths_by_ext['.star']
    return zip_mrc_star_to_crates(mrc_files, star_files)


readers = {
    '.mrc': mrc_reader,
    '.star': star_reader,
    'zip_mrc_star': zip_mrc_star_reader,
}


def dispatch(files):
    """
    guess the appropriate reader function to use based on the file paths provided
    """
    # split by extension
    files_by_ext = {}
    for file_path in files:
        if file_path.suffix not in files_by_ext:
            files_by_ext[file_path.suffix] = []
        files_by_ext[file_path.suffix].append(file_path)

    filetypes = set(files_by_ext.keys())
    files = set(files)

    reader = None
    if len(filetypes) == 1:
        reader = readers[filetypes.pop()]
    elif set(files_by_ext.keys()) == {'.mrc', '.star'}:
        reader = readers['zip_mrc_star']

    if reader is None:
        raise ValueError(f'could not guess how to open the given path(s)')

    return reader(files_by_ext)


def read(paths):
    """
    guess how to interpret the given paths and load the data into the appropriate
    peepingtom data structure.
    """
    files = find_files(paths)
    return dispatch(files)
