import einops
import napari
import numpy as np
from scipy.spatial.transform import Rotation


def invert_xyz(arr):
    return arr[..., ::-1]


def generate_vectors(coords, orientations):
    """Generate basis vectors and relative colors for napari."""
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


def layer_tuples_to_layers(layer_tuples):
    return [
        getattr(napari.layers, ltype.capitalize())(data, **kwargs)
        for data, kwargs, ltype in layer_tuples
    ]
