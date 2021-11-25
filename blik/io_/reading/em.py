import logging

import emfile
import dask.array as da

from ...datablocks import ImageBlock
from ..utils import guess_name


logger = logging.getLogger(__name__)


def read_em(image_path, name_regex=None, lazy=True, **kwargs):
    """
    read an em file and return an ImageBlock
    """
    name = guess_name(image_path, name_regex)

    if lazy:
        header, data = emfile.read(image_path, mmap=True)
        data = da.from_array(data)
    else:
        header, data = emfile.read(image_path)

    pixel_size = header['OBJ']

    ib = ImageBlock(data=data, pixel_size=pixel_size, name=name)
    logger.debug(f'succesfully read "{image_path}", {lazy=}')
    return ib
