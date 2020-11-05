import re
from pathlib import Path
import numpy as np
import mrcfile
import starfile
from eulerangles import euler2matrix

from data import Particles, Image, DataBlock


def _path(path):
    """
    clean up a path
    """
    return Path(path).expanduser().resolve()


def guess_name(thing):
    """
    guess an appropriate name based on the input
    thing: string or stringifiable or list containing such
    """
    name = 'NoName'
    if isinstance(thing, list):
        raise NotImplementedError('no way to guess a name from a list yet')
    elif match := re.search('TS_\d+', str(thing)):
        name = match.group(0)
    return name


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
        data.append(mrcfile.open(_path(image))[0][0])
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


def read_starfiles(starfile_paths, sort=True, data_columns=None):
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

    data = []
    for raw_name, star_df in dataframes:
        # guess a name for the data
        name = guess_name(raw_name)
        # get coordinates from dataframe in zyx order
        coords = []
        for axis in 'ZYX':
            ax = np.array(star_df[f'rlnCoordinate{axis}'] + star_df.get(f'rlnOrigin{axis}', 0))
            coords.append(ax)
        coords = np.stack(coords, axis=1)

        # get orientations as euler angles and transform it into rotation matrices
        orient_euler = star_df[['rlnAngleRot', 'rlnAngleTilt', 'rlnAnglePsi']].to_numpy()
        orient_matrices = euler2matrix(orient_euler, axes='ZYZ', intrinsic=True, positive_ccw=True)

        if data_columns is None:
            data_columns = []
        columns = [col for col in data_columns if col in star_df.columns]
        properties = star_df[columns]

        data.append((name, coords, orient_matrices, properties))
    return data


def zip_data_to_blocks(mrc_paths=[], star_paths=[], sort=True, data_columns=None):
    """
    reads n mrc files and starfiles assuming they contain data relating to the same 3D volumes
    returns n data_blocks
    """
    star_dfs = read_starfiles(star_paths, sort, data_columns)
    # this check must be done after loading starfiles, but better before images
    if not isinstance(mrc_paths, list):
        # needed for length check
        mrc_paths = [mrc_paths]
    if len(mrc_paths) != len(star_dfs):
        raise ValueError(f'number of images ({len(mrc_paths)}) is different from starfile datasets ({len(star_dfs)})')
    images = read_images(mrc_paths, sort)

    blocks = []
    # loop through everything
    for image, (name, coords, ori_matrix, properties) in zip(images, star_dfs):
        data_block = DataBlock()
        data_block.append(Image(image))
        # denormalize if necessary (not index column) by multiplying by the shape of images
        if coords.max() <= 1:
            coords *= image.shape
        data_block.append(Particles(coords, ori_matrix, properties=properties))
        blocks.append(data_block)

    return blocks
