import einops
import numpy as np
from scipy.spatial.transform import Rotation


def generate_vectors(coords, orientations):
    mat = Rotation.concatenate(orientations).as_matrix()
    basis_vecs = einops.rearrange(mat, "batch a b -> b batch a")
    vec_data = np.empty((len(coords) * 3, 2, 3))
    vec_color = np.empty((len(coords) * 3, 3))
    for idx, vecs in enumerate(basis_vecs):
        color = np.zeros(3)
        color[idx] = 1  # rgb
        vec_data[idx::3] = np.stack([coords, vecs], axis=1)
        vec_color[idx::3] = color
    return vec_data, vec_color
