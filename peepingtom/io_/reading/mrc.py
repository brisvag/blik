import logging

import mrcfile

from ...datablocks import ImageBlock
from ..utils import guess_name
from numpy.lib.recfunctions import structured_to_unstructured


logger = logging.getLogger(__name__)


def read_mrc(image_path, name_regex=None, mmap=False, lazy=True, **kwargs):
    """
    read an mrc file and return an ImageBlock
    """
    name = guess_name(image_path, name_regex)

    def loader(imageblock):
        if mmap is True:
            mrc = mrcfile.mmap(image_path)
        else:
            mrc = mrcfile.open(image_path)
        imageblock.data = mrc.data
        pixel_size = structured_to_unstructured(mrc.voxel_size)[::-1]
        imageblock.pixel_size = pixel_size

    ib = ImageBlock(lazy_loader=loader, name=name)
    if not lazy:
        ib.load()
    logger.debug(f'succesfully read "{image_path}", {lazy=}, {mmap=}')
    return ib
