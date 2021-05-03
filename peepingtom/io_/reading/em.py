import emfile

from ...datablocks import ImageBlock
from ..utils import guess_name


def read_em(image_path, name_regex=None, lazy=True, **kwargs):
    """
    read an em file and return an ImageBlock
    """
    name = guess_name(image_path, name_regex)

    def data():
        return emfile.read(image_path)[1]

    if not lazy:
        data = data()
    return ImageBlock(data, name=name)
