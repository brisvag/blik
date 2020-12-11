import emfile

from ...utils import _path


def write_em(imageblock, file_path, overwrite=False):
    """
    write an image block to disk as an .em file
    """
    path = str(_path(file_path))
    if not path.endswith('.em'):
        path = f'{path}.em'
    emfile.write(path, imageblock.data, header_params={}, overwrite=overwrite)
