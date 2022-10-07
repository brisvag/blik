from __future__ import annotations

from magicgui import magicgui
import numpy as np
from scipy.interpolate import splprep, splev
from scipy.spatial.transform import Rotation
import napari

from cryotypes.poseset import validate_poseset_dataframe


def sample_equidistant_spline(points, distance, sampling=10000):
    tck, u = splprep([*points.T])
    sample_points = np.linspace(0, 1, sampling)
    sampled = np.stack(splev(sample_points, tck)).T
    pairwise_diff = sampled - np.roll(sampled, -1, axis=0)
    pairwise_dist = np.linalg.norm(pairwise_diff, axis=1)
    modsum = np.mod(np.cumsum(pairwise_dist), distance)
    good = modsum > np.roll(modsum, -1)
    deriv = np.stack(splev(sample_points[good], tck, der=1)).T
    directions = deriv / np.linalg.norm(deriv, axis=1).reshape(-1, 1)
    # vectors = np.stack([sampled[good], directions], axis=1)
    return sampled[good], directions


@magicgui(
    auto_call=True,
)
def filament_model(source_layer: napari.layers.Points, distance: float = 1, sampling: int = 10000) -> list[napari.types.FullLayerData]:
    if source_layer is None:
        return
    points, vectors = sample_equidistant_spline(source_layer.data)
    rots = mat_from_dir(vectors)


def construct_rotations_from_directions(directions):
    rots = []
    for dir in directions:
        rot = Rotation.align_vectors([[0, 0, 1]], dir[np.newaxis])[0]
        rots.append(rot)
    return Rotation.concatenate(rots)


def mat_from_dir(directions):
    directions /= np.linalg.norm(directions, axis=-1, keepdims=True)  # (n, 1)

    random_vector = np.random.random((1, 3))

    y_vectors = np.cross(directions, random_vector)
    y_vectors /= np.linalg.norm(y_vectors, axis=-1, keepdims=True)  # (n, 1)

    x_vectors = np.cross(y_vectors, directions)
    x_vectors /= np.linalg.norm(x_vectors, axis=-1, keepdims=True)  # (n, 1)

    rotation_matrices = np.empty(shape=(len(directions), 3, 3))
    rotation_matrices[:, :, 0] = x_vectors
    rotation_matrices[:, :, 1] = y_vectors
    rotation_matrices[:, :, 2] = directions

    return Rotation.from_matrix(rotation_matrices)
