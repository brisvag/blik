import numpy as np
from scipy.spatial.transform import Rotation


def generate_vectors(coords, orientations):
    orientations = Rotation.concatenate(orientations)
    vec_data = np.empty((len(coords) * 3, 2, 3))
    vec_color = np.empty((len(coords) * 3, 3))
    for idx, (ax, color) in enumerate(zip('xyz', 'rgb')):
        basis = np.zeros(3)
        basis[idx] = 1  # also acts as color (rgb)
        basis_rot = orientations.apply(basis)[:, ::-1]  # order is zyx in napari
        vec_data[idx::3] = np.stack([coords, basis_rot], axis=1)
        vec_color[idx::3] = basis
    return vec_data, vec_color
