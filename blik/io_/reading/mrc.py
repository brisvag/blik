import logging

import mrcfile
import dask.array as da
import numpy as np

from ...datablocks import ImageBlock
from ..utils import guess_name
from numpy.lib.recfunctions import structured_to_unstructured


logger = logging.getLogger(__name__)


def read_mrc(image_path, name_regex=None, lazy=True, **kwargs):
    """
    read an mrc file and return an ImageBlock
    """
    name = guess_name(image_path, name_regex)

    with mrcfile.mmap(image_path) as mrc:
        if lazy:
            data = da.from_array(mrc.data)
        else:
            data = np.asarray(mrc.data)

        pixel_size = structured_to_unstructured(mrc.voxel_size)[::-1]

    ib = ImageBlock(data=data, pixel_size=pixel_size, name=name)
    logger.debug(f'succesfully read "{image_path}", {lazy=}')
    return ib
