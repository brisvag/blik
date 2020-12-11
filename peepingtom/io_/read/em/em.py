import emfile

from ....core import ImageBlock
from ...utils import guess_name


def read_em(image_path, name_regex=None, **kwargs):
    """
    read an em file and return an ImageBlock
    """
    name = guess_name(image_path, name_regex)
    return ImageBlock(emfile.read(image_path)[1], name=name)
