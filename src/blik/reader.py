import warnings
from importlib.metadata import version
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


def _construct_positions_layer(
    coords, features, scale, exp_id, p_id, source, name_suffix, **points_kwargs
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
            "scale": [scale] * 3,
            "shading": "spherical",
            "antialiasing": 0,
            "border_width": 0,
            "metadata": {"experiment_id": exp_id, "p_id": p_id, "source": source},
            "out_of_slice_display": True,
            "projection_mode": "all",
            # "axis_labels": ('z', 'y', 'x'),
            "units": 'angstrom',
            **points_kwargs,
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
            "projection_mode": "all",
            # "axis_labels": ('z', 'y', 'x'),
            "units": 'angstrom',
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
    **points_kwargs,
):
    """
    Constructs particle layer tuples from particle data.

    Coords should be still in xyz order (will be flipped to zyx in output).
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
        **points_kwargs,
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
        warnings.warn(f"unknown pixel spacing for particles '{particles.experiment_id}'; setting to 1 Angstrom.", stacklevel=2)
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


def construct_image_layer_tuple(
    data,
    scale,
    exp_id,
    stack=False,
    source="",
    **image_kwargs,
):
    return (
        data,
        {
            "name": f"{exp_id} - image",
            "scale": [scale] * 3,
            "metadata": {"experiment_id": exp_id, "stack": stack, "source": source},
            "interpolation2d": "spline36",
            "interpolation3d": "linear",
            "blending": "translucent",
            "projection_mode": "mean",
            "depiction": "plane",
            "plane": {"thickness": 5, "position": np.array(data.shape) / 2},
            "rendering": "average",
            # "axis_labels": ('z', 'y', 'x'),
            "units": 'angstrom',
            **image_kwargs,
        },
        "image",
    )


def read_image(image):
    return construct_image_layer_tuple(
        data=image.data,
        scale=image.pixel_spacing,
        exp_id=image.experiment_id,
        stack=image.stack,
        source=image.source,
    )


def construct_segmentation_layer_tuple(
    data,
    scale,
    exp_id,
    stack=False,
    source="",
    **labels_kwargs,
):
    return (
        data,
        {
            "name": f"{exp_id} - segmentation",
            "scale": [scale] * 3,
            "metadata": {"experiment_id": exp_id, "stack": stack, "source": source},
            "blending": "translucent",
            # "axis_labels": ('z', 'y', 'x'),
            "units": 'angstrom',
            **labels_kwargs,
        },
        "labels",
    )


def read_segmentation(image):
    return construct_segmentation_layer_tuple(
        data=image.data,
        scale=image.pixel_spacing,
        exp_id=image.experiment_id,
        stack=image.stack,
        source=image.source,
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
            # "axis_labels": ('z', 'y', 'x'),
            "units": 'angstrom',
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
            # "axis_labels": ('z', 'y', 'x'),
            "units": 'angstrom',
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

    obj_list = cryohub.read(*cryohub_paths, **kwargs)
    # sort so we get images first, better for some visualization circumstances
    for obj in sorted(obj_list, key=lambda x: not isinstance(x, ImageProtocol)):
        if not obj.pixel_spacing:
            warnings.warn(f"unknown pixel spacing for {obj.__class__.__name__} '{obj.experiment_id}'; setting to 1 Angstrom.", stacklevel=2)
            obj.pixel_spacing = 1
        if isinstance(obj, ImageProtocol):
            if np.issubdtype(obj.data.dtype, np.integer) and np.iinfo(obj.data.dtype).bits == 8:
                layers.append(read_segmentation(obj))
            else:
                layers.append(read_image(obj))
        elif isinstance(obj, PoseSetProtocol):
            layers.extend(read_particles(obj))

    for lay in layers:
        lay[1]["visible"] = False  # speed up loading
    return layers or None
