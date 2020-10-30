import re
from pathlib import Path
import numpy as np
import napari
import starfile
from eulerangles import euler2matrix


def _path(path):
    return Path(path).expanduser().resolve()

def guess_names(thing):
    """
    guess an appropriate name based on the input
    thing: string or stringifiable or list containing such
    """
    names = []
    if not isinstance(thing, list):
        thing = [thing]
    for string in thing:
        if match := re.search('TS_\d+', str(thing)):
            names.append(match.group(0))
        else:
            names.append('NoName')
    return names

def read_images(image_paths):
    data = []
    if not isinstance(image_paths, list):
        image_paths = [image_paths]
    for image in image_paths:
        data.append(napari.plugins.io.read_data_with_plugins(_path(image))[0][0])
    return data


def _read_starfile(star_path):
    df = starfile.read(_path(star_path))
    if 'rlnMicrographName' in df.columns:
        groups = df.groupby('rlnMicrographName')
        return [(name, sub_df) for name, sub_df in groups]
    else:
        return [(star_path, df)]


def read_starfiles(starfile_paths):
    dataframes = []
    if not isinstance(starfile_paths, list):
        starfile_paths = [starfile_paths]
    for star in starfile_paths:
        dataframes.extend(_read_starfile(star))

    data = []
    for raw_name, star_df in dataframes:
        # guess a name for the data
        name = guess_names(raw_name)
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

        data.append((name, coords, orient_vectors))
    return data
