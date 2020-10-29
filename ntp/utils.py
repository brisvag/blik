from pathlib import Path
import numpy as np
import napari
import starfile
from eulerangles import euler2matrix


def _path(path):
    return Path(path).expanduser().resolve()


def read_images(image_paths):
    data = []
    if isinstance(image_paths, list):
        for image in image_paths:
            data.append(napari.plugins.io.read_data_with_plugins(_path(image))[0][0])
    else:
        data.append(napari.plugins.io.read_data_with_plugins(_path(image_paths))[0][0])
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
    if isinstance(starfile_paths, list):
        for star in starfile_paths:
            dataframes.extend(_read_starfile(star))
    else:
        dataframes.extend(_read_starfile(starfile_paths))

    data = []
    for name, star_df in dataframes:
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
