import emfile

from ...datablocks import ImageBlock
from ..utils import guess_name


def read_em(image_path, name_regex=None, lazy=True, **kwargs):
    """
    read an em file and return an ImageBlock
    """
    name = guess_name(image_path, name_regex)

    def loader(imageblock):
        header, data = emfile.read(image_path)
        imageblock.data = data
        imageblock.pixel_size = header['OBJ']

    ib = ImageBlock(lazy_loader=loader, name=name)
    if not lazy:
        ib.load()
    return ib
