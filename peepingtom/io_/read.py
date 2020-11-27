from .utils import _path, known_filetypes


def find_files(path, recursive=False):
    path = _path(path)

    if not path.exists():
        raise FileNotFoundError(f'{path} does not exist')

    files = []
    if path.is_file():
        print(path)
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


def get_reader(files):
    """
    guess the appropriate reader function to use based on the file paths provided
    """
    if len(files) == 1:
        return reader[files[0].extension]
    else:
        # split by extension
        files_by_ext = {ext: [] for ext in known_filetypes}
        for file_path in files:
            files_by_ext.append(file_path)


def read(paths):
    """
    guess how to interpret the given paths and load the data into the appropriate
    peepingtom data structure.
    """
    files = find_files(paths)

reader = {
    '.mrc': mrc_reader,
    '.star': star_reader,

}
