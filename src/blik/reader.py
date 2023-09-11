import warnings
from pathlib import Path
from uuid import uuid1

import cryohub
import numpy as np
import pandas as pd
from cryotypes.image import ImageProtocol
from cryotypes.poseset import PoseSetProtocol
from scipy.spatial.transform import Rotation

from .utils import generate_vectors, invert_xyz


def get_reader(path):
    return read_layers


def _construct_positions_layer(coords, features, scale, exp_id, p_id, source):
    feat_defaults = (
        pd.DataFrame(features.iloc[-1].to_dict(), index=[0])
        if len(features)
        else pd.DataFrame()
    )
    feat_defaults["orientation"] = Rotation.identity()
    return (
        coords,
        {
            "name": f"{exp_id} - particle positions",
            "features": features,
            "feature_defaults": feat_defaults,
            "face_color": "teal",
            "size": 5,
            "edge_width": 0,
            "scale": [scale] * 3,
            "shading": "spherical",
            "antialiasing": 0,
            "metadata": {"experiment_id": exp_id, "p_id": p_id, "source": source},
            "out_of_slice_display": True,
        },
        "points",
    )


def _construct_orientations_layer(coords, features, scale, exp_id, p_id, source):
    if coords is None:
        vec_data = None
        vec_color = "blue"
    else:
        vec_data, vec_color = generate_vectors(
            invert_xyz(coords), features["orientation"]
        )
        vec_data = invert_xyz(vec_data)
    return (
        vec_data,
        {
            "name": f"{exp_id} - particle orientations",
            "edge_color": vec_color,
            "length": 50 / np.array(scale),
            "scale": [scale] * 3,
            "metadata": {"experiment_id": exp_id, "p_id": p_id, "source": source},
            "out_of_slice_display": True,
        },
        "vectors",
    )


def construct_particle_layer_tuples(
    coords, features, scale, exp_id, p_id=None, source=""
):
    """
    Constructs particle layer tuples from particle data.

    Data is assumed to already by in zyx napari format, while features is
    the normal poseset dataframe.
    """
    # unique id so we can connect layers safely
    p_id = p_id if p_id is not None else uuid1()

    if features is None:
        features = pd.DataFrame()

    if "orientation" not in features.columns:
        features["orientation"] = np.array(
            [] if coords is None else Rotation.identity(len(coords))
        )

    # divide by scale top keep constant size. TODO: remove after vispy 0.12 which fixes this
    pos = _construct_positions_layer(coords, features, scale, exp_id, p_id, source)
    ori = _construct_orientations_layer(coords, features, scale, exp_id, p_id, source)

    # invert order for convenience (latest added layer is selected)
    return [ori, pos]


def read_particles(particles):
    """Takes a valid poseset and converts it into napari layers."""
    # order is zyx in napari
    coords = invert_xyz(particles.position)

    if particles.features is not None:
        features = particles.features.copy(deep=False)
    else:
        features = pd.DataFrame()

    px_size = particles.pixel_spacing
    if not px_size:
        warnings.warn("unknown pixel spacing, setting to 1 Angstrom")
        px_size = 1

    if particles.shift is not None:
        shifts = invert_xyz(particles.shift)
        coords = coords + shifts
        shift_cols = ["shift_z", "shift_y", "shift_x"]
        features[shift_cols] = shifts
    if particles.orientation is not None:
        features["orientation"] = np.asarray(particles.orientation)

    return construct_particle_layer_tuples(
        coords, features, px_size, particles.experiment_id, particles.source
    )


def read_image(image):
    px_size = image.pixel_spacing
    if not px_size:
        warnings.warn("unknown pixel spacing, setting to 1 Angstrom")
        px_size = 1
    return (
        image.data,
        {
            "name": f"{image.experiment_id} - image",
            "scale": [px_size] * image.data.ndim,
            "metadata": {"experiment_id": image.experiment_id, "stack": image.stack},
            "interpolation2d": "spline36",
            "interpolation3d": "linear",
            "rendering": "average",
            "depiction": "plane",
            "blending": "translucent",
            "plane": {"thickness": 5},
        },
        "image",
    )


def read_surface_picks(path):
    lines = []
    with open(path, "rb") as f:
        scale = np.load(f)
        surf_id = np.load(f)
        edge_color_cycle = np.load(f)
        while True:
            try:
                lines.append(np.load(f))
            except ValueError:
                break
        exp_id = f.read().decode()

    return (
        lines,
        {
            "name": f"{exp_id} - surface lines",
            "edge_width": 50 / scale[0],
            "metadata": {"experiment_id": exp_id},
            "scale": scale,
            "features": {"surface_id": surf_id},
            "feature_defaults": {"surface_id": surf_id.max() + 1},
            "edge_color_cycle": edge_color_cycle,
            "edge_color": "surface_id",
            "shape_type": "path",
            "ndim": 3,
        },
        "shapes",
    )


def read_surface(path):
    with open(path, "rb") as f:
        scale = np.load(f)
        # TODO: needs to exposed in napari
        # colormap = np.load(f)
        data = tuple(np.load(f) for _ in range(3))
        exp_id = f.read().decode()

    return (
        data,
        {
            "name": f"{exp_id} - surface",
            "metadata": {"experiment_id": exp_id},
            "shading": "smooth",
            "scale": scale,
            # TODO: needs to exposed in napari
            # colormap=colormap
        },
        "surface",
    )


def read_layers(*paths, **kwargs):
    layers = []
    cryohub_paths = []
    for path in paths:
        path = Path(path)
        if path.suffix == ".picks":
            layers.append(read_surface_picks(path))
        if path.suffix == ".surf":
            layers.append(read_surface(path))
        else:
            cryohub_paths.append(path)

    data_list = cryohub.read(*cryohub_paths, **kwargs)
    # sort so we get images first, better for some visualization circumstances
    for data in sorted(data_list, key=lambda x: not isinstance(x, ImageProtocol)):
        if isinstance(data, ImageProtocol):
            layers.append(read_image(data))
        elif isinstance(data, PoseSetProtocol):
            layers.extend(read_particles(data))

    for lay in layers:
        lay[1]["visible"] = False  # speed up loading
    return layers or None
