"""
Functions to read raw data files and return DataBlocks
"""

from pathlib import Path
from typing import Union, List, Tuple

import mrcfile
import pandas as pd
import starfile

from ..core import ImageBlock, ParticleBlock
from .utils import _path


def mrc_to_imageblock(image_paths: Union[str, List[str], Path], sort=True) -> List[ImageBlock]:
    """
    read any number of mrc files and return as a list of ImageBlock objects

    Parameters
    ----------
    image_path : Path-like or list of Path-like objects containing paths to mrc files
    sort : bool, should the returned be sorted by the filenames?

    Returns list of np.ndarray objects containing image data
    -------

    """
    if not isinstance(image_paths, list):
        image_paths = [image_paths]
    if sort:
        image_paths = sorted(image_paths)

    data = [ImageBlock(mrcfile.open(_path(image)).data) for image in image_paths]
    return data


def _read_relion_star_file(star_path) -> List[Tuple[str, pd.DataFrame]]:
    """
    read a single star file and return a list containing each dataset found in the file,
    as a separate (name, dataframe) tuple

    Parameters
    ----------
    star_path : Path-like object containing the path to a relion format star file

    Returns list of (star_path, pd.DataFrame) tuples
    -------

    """

    df = starfile.read(_path(star_path))
    if 'rlnMicrographName' in df.columns:
        groups = df.groupby('rlnMicrographName')
        return [(str(name), sub_df) for name, sub_df in groups]
    else:
        return [(str(star_path), df)]


def data_star_to_particleblock(star_paths: Union[str, List[str], Path], sort=True,
                               data_columns=None, mode='relion') -> List[ParticleBlock]:
    """
    read a number of STAR files and return a list of ParticleBlock objects

    Parameters
    ----------
    star_path : Path-like or list of Path-like objects containing paths to RELION *_data.star type STAR files
    sort : bool, should resulting list be ordered alphabetically by filename
    data_columns :
    mode : str containing valid mode for *_data.star type STAR files

    Returns list of ParticleBlock objects
    -------

    """
    if not isinstance(star_paths, list):
        star_paths = [star_paths]
    if sort:
        star_paths = sorted(star_paths)

    dataframes = []
    for star in star_paths:
        dataframes.extend(_read_relion_star_file(star))

    particles = [ParticleBlock.from_dataframe(star_df, data_columns=data_columns, mode=mode)
                 for raw_name, star_df in dataframes]
    return particles
