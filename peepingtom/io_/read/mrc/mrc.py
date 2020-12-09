import mrcfile

from ...core import ImageBlock


def read_mrc(image_path):
    """
    read an mrc file and return an ImageBlock
    """
    return ImageBlock(mrcfile.open(image_path).data)