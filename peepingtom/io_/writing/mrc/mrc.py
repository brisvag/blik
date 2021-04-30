import mrcfile

from ...utils import _path


def write_mrc(imageblock, file_path, overwrite=False):
    """
    write an image block to disk as an .mrc file
    """
    path = str(_path(file_path))
    if not path.endswith('.mrc'):
        path = f'{path}.mrc'
    mrcfile.new(path, imageblock.data, overwrite=overwrite)
