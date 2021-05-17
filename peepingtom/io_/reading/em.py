import emfile

from ...datablocks import ImageBlock
from ..utils import guess_name


def read_em(image_path, name_regex=None, lazy=True, **kwargs):
    """
    read an em file and return an ImageBlock
    """
    name = guess_name(image_path, name_regex)

    data = emfile.read(image_path)[1]

    return ImageBlock(data=data, ndim=data.ndim, name=name)
