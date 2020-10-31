import re
from pathlib import Path
import numpy as np
import napari
import starfile
from eulerangles import euler2matrix


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
    read any number of image files using napari plugins, and return the data
    as list of numpy array
    """
    data = []
    if not isinstance(image_paths, list):
        image_paths = [image_paths]
    if sort:
        image_paths = sorted(image_paths)
    for image in image_paths:
        data.append(napari.plugins.io.read_data_with_plugins(_path(image))[0][0])
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


def read_starfiles(starfile_paths, sort=True, additional_columns=None):
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
        # get orientations as unit vectors centered on the origin
        orient_vectors = np.einsum('ijk,j->ik', orient_matrices, [0, 0, 1])
        # reslice them in zyx order
        orient_vectors = orient_vectors[:, [2, 1, 0]]

        add_data = {}
        if additional_columns is None:
            additional_columns = []
        for column in additional_columns:
            add_data[column] = np.array(star_df[column])

        data.append((name, coords, orient_vectors, add_data))
    return data
