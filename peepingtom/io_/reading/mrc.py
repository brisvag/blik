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
    mrc = mrcfile.open(image_path, header_only=True)
    pixel_size = structured_to_unstructured(mrc.voxel_size)[::-1]
    shape = mrc.header[['nz', 'ny', 'nx']]
    shape = tuple(int(x) for x in structured_to_unstructured(shape))
    if shape[0] == 1:
        ndim = 2
    else:
        ndim = 3

    def loader():
        if mmap is True:
            mrc = mrcfile.mmap(image_path).data
        else:
            mrc = mrcfile.open(image_path).data
        return mrc

    logger.debug(f'succesfully read "{image_path}", {lazy=}, {mmap=}')
    if lazy:
        return ImageBlock(loader, pixel_size=pixel_size, name=name, shape=shape, ndim=ndim)

