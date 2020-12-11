import mrcfile

from ....core import ImageBlock
from ...utils import guess_name


def read_mrc(image_path, name_regex=None, **kwargs):
    """
    read an mrc file and return an ImageBlock
    """
    name = guess_name(image_path, name_regex)
    return ImageBlock(mrcfile.open(image_path).data, name=name)
