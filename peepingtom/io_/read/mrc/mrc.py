import mrcfile

from ....datablocks import ImageBlock
from ...utils import guess_name
from numpy.lib.recfunctions import structured_to_unstructured


def read_mrc(image_path, name_regex=None, **kwargs):
    """
    read an mrc file and return an ImageBlock
    """
    name = guess_name(image_path, name_regex)
    mrc = mrcfile.mmap(image_path)
    pixel_size = structured_to_unstructured(mrc.voxel_size)[::-1]
    return ImageBlock(mrc.data, pixel_size=pixel_size, name=name)
