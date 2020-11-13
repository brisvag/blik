from typing import Union, List
from pathlib import Path

import numpy as np
import mrcfile
import starfile
from eulerangles import euler2matrix

from ..base import ImageBlock, ParticleBlock, DataCrate
from .utils import _path, guess_name


def read_images(image_paths, sort=True):
    """
    read any number of mrc files and return the data as list of numpy arrays
    """
    data = []
    if not isinstance(image_paths, list):
        image_paths = [image_paths]
    if sort:
        image_paths = sorted(image_paths)
    for image in image_paths:
        data.append(ImageBlock(mrcfile.open(_path(image)).data))
    return data


def _read_starfile(star_path):
    """
    read a single star file and return a list containing each dataset
    found in the file, as a separate (name, dataframe) tuple
    """
    df = starfile.read(_path(star_path))
    if 'rlnMicrographName' in df.columns:
        groups = df.groupby('rlnMicrographName')
        return [(name, sub_df) for name, sub_df in groups]
    else:
        return [(star_path, df)]


def starfiles_to_particles(starfile_paths, sort=True, data_columns=None, mode='relion'):
    """
    read a number of star files and return a list of each dataset found
    as particle coordinates, orientations and additional data
    """
    dataframes = []
    if not isinstance(starfile_paths, list):
        starfile_paths = [starfile_paths]
    if sort:
        starfile_paths = sorted(starfile_paths)
    for star in starfile_paths:
        dataframes.extend(_read_starfile(star))

    particles = []
    for raw_name, star_df in dataframes:
        particles.append(ParticleBlock.from_dataframe(star_df, mode, data_columns=data_columns))
    return particles


# def zip_data_to_blocks(mrc_paths=[], star_paths=[], sort=True, data_columns=None):
    # """
    # reads n mrc files and starfiles assuming they contain data relating to the same 3D volumes
    # returns n data_blocks
    # """
    # star_dfs = read_starfiles(star_paths, sort, data_columns)
    # # this check must be done after loading starfiles, but better before images
    # if not isinstance(mrc_paths, list):
        # # needed for length check
        # mrc_paths = [mrc_paths]
    # if len(mrc_paths) != len(star_dfs):
        # raise ValueError(f'number of images ({len(mrc_paths)}) is different from starfile datasets ({len(star_dfs)})')
    # images = read_images(mrc_paths, sort)

    # blocks = []
    # # loop through everything
    # for image, (name, coords, ori_matrix, properties) in zip(images, star_dfs):
        # data_block = DataBlock()
        # data_block.append(Image(image))
        # # denormalize if necessary (not index column) by multiplying by the shape of images
        # if coords.max() <= 1:
            # coords *= image.shape
        # data_block.append(ParticleBlock(coords, ori_matrix, properties=properties))
        # blocks.append(data_block)

    # return blocks


def star_to_crates(star_files: Union[Path, str, list], data_columns: List[str] = [], mode='relion'):
    """
    Reads an arbitrary number of star files
    Returns a list of DataCrates
    """
    particles = starfiles_to_particles(starfile_paths=star_files, data_columns=data_columns, mode=mode)

    return [DataCrate([particle]) for particle in particles]


def images_to_crates(image_paths):
    return [DataCrate([image]) for image in read_images(image_paths)]
