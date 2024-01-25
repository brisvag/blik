import warnings
from importlib.metadata import version
from pathlib import Path
from uuid import uuid1

import cryohub
import numpy as np
import pandas as pd
from cryotypes.image import ImageProtocol
from cryotypes.poseset import PoseSetProtocol
from packaging.version import parse as parse_version
from scipy.spatial.transform import Rotation

from .utils import generate_vectors, invert_xyz

NAPARI_050 = parse_version(version("napari")) >= parse_version("0.5.0a")


def get_reader(path):
    return read_layers


def _construct_positions_layer(
    coords, features, scale, exp_id, p_id, source, name_suffix, **pt_kwargs
):
    feat_defaults = (
        pd.DataFrame(features.iloc[-1].to_dict(), index=[0])
        if len(features)
        else pd.DataFrame()
    )
    feat_defaults["orientation"] = np.array(Rotation.identity(), dtype=object)
    if coords is not None:
        coords = invert_xyz(coords)
    return (
        coords,
        {
            "name": f"{exp_id} - {name_suffix} positions",
            "features": features,
            "feature_defaults": feat_defaults,
            "face_color": "teal",
            "size": 5 / scale,
            "edge_width": 0,
            "scale": [scale] * 3,
            "shading": "spherical",
            "antialiasing": 0,
            "metadata": {"experiment_id": exp_id, "p_id": p_id, "source": source},
            "out_of_slice_display": True,
            **pt_kwargs,
            **({"projection_mode": "all"} if NAPARI_050 else {}),
        },
        "points",
    )


def _construct_orientations_layer(
    coords, features, scale, exp_id, p_id, source, name_suffix
):
    if coords is None:
        vec_data = None
        vec_color = "blue"
    else:
        vec_data, vec_color = generate_vectors(coords, features["orientation"])
        vec_data = invert_xyz(vec_data)  # napari works in zyx order
    return (
        vec_data,
        {
            "name": f"{exp_id} - {name_suffix} orientations",
            "edge_color": vec_color,
            "length": 100 / np.array(scale),
            "edge_width": 10 / np.array(scale),
            "scale": [scale] * 3,
            "metadata": {"experiment_id": exp_id, "p_id": p_id, "source": source},
            "vector_style": "arrow",
            "out_of_slice_display": True,
            **({"projection_mode": "all"} if NAPARI_050 else {}),
        },
        "vectors",
    )


def construct_particle_layer_tuples(
    coords,
    features,
    scale,
    exp_id,
    p_id=None,
    source="",
    name_suffix="",
    **pt_kwargs,
):
    """
    Constructs particle layer tuples from particle data.

    Data should be still in xyz format (will be flipped to zyx).
    """
    # unique id so we can connect layers safely
    p_id = p_id if p_id is not None else uuid1()

    if features is None:
        features = pd.DataFrame()

    if "orientation" not in features.columns:
        features["orientation"] = np.array(
            [] if coords is None else Rotation.identity(len(coords)), dtype=object
        )

    # divide by scale top keep constant size. TODO: remove after vispy 0.12 which fixes this
    pos = _construct_positions_layer(
        coords=coords,
        features=features,
        scale=scale,
        exp_id=exp_id,
        p_id=p_id,
        source=source,
        name_suffix=name_suffix,
        **pt_kwargs,
    )
    ori = _construct_orientations_layer(
        coords=coords,
        features=features,
        scale=scale,
        exp_id=exp_id,
        p_id=p_id,
        name_suffix=name_suffix,
        source=source,
    )

    # ori should be last, or the auto-update feedback loop messes up the orientations
    # when existing layers are updated from a new run
    return [pos, ori]


def read_particles(particles, name_suffix="particle"):
    """Takes a valid poseset and converts it into napari layers."""
    coords = particles.position

    if particles.features is not None:
        features = particles.features.copy(deep=False)
    else:
        features = pd.DataFrame()

    px_size = particles.pixel_spacing
    if not px_size:
        warnings.warn("unknown pixel spacing, setting to 1 Angstrom", stacklevel=2)
        px_size = 1

    if particles.shift is not None:
        coords = coords + particles.shift
        shift_cols = ["shift_x", "shift_y", "shift_z"]
        features[shift_cols] = particles.shift
    if particles.orientation is not None:
        features["orientation"] = np.asarray(particles.orientation, dtype=object)

    return construct_particle_layer_tuples(
        coords=coords,
        features=features,
        scale=px_size,
        exp_id=particles.experiment_id,
        source=particles.source,
        name_suffix=name_suffix,
    )


def read_image(image):
    px_size = image.pixel_spacing
    if not px_size:
        warnings.warn("unknown pixel spacing, setting to 1 Angstrom", stacklevel=2)
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
            **({"projection_mode": "mean"} if NAPARI_050 else {}),
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
