import warnings
from pathlib import Path
from uuid import uuid1

import numpy as np
from cryohub import read
from cryotypes.image import Image
from cryotypes.poseset import PoseSet
from cryotypes.poseset import PoseSetDataLabels as PSDL

from .utils import generate_vectors, invert_xyz


def get_reader(path):
    return read_layers


def _construct_positions_layer(coords, features, scale, exp_id, p_id):
    return (
        coords,
        dict(
            name=f"{exp_id} - particle positions",
            features=features,
            face_color="teal",
            size=50,  # TODO: this will be fixed by vispy 0.12!
            edge_width=0,
            scale=[scale] * 3,
            shading="spherical",
            antialiasing=0,
            metadata={"experiment_id": exp_id, "p_id": p_id},
            out_of_slice_display=True,
        ),
        "points",
    )


def _construct_orientations_layer(coords, features, scale, exp_id, p_id):
    if coords is None:
        vec_data = None
        vec_color = "blue"
    else:
        vec_data, vec_color = generate_vectors(
            invert_xyz(coords), features[PSDL.ORIENTATION]
        )
        vec_data = invert_xyz(vec_data)
    return (
        vec_data,
        dict(
            name=f"{exp_id} - particle orientations",
            edge_color=vec_color,
            length=50 / scale,
            scale=[scale] * 3,
            metadata={"experiment_id": exp_id, "p_id": p_id},
            out_of_slice_display=True,
        ),
        "vectors",
    )


def construct_particle_layer_tuples(coords, features, scale, exp_id, p_id=None):
    """
    Constructs particle layer tuples from particle data.

    Data is assumed to already by in zyx napari format, while features is
    the normal poseset dataframe.
    """
    # unique id so we can connect layers safely
    p_id = p_id if p_id is not None else uuid1()

    # divide by scale top keep constant size. TODO: remove after vispy 0.12 which fixes this
    pos = _construct_positions_layer(coords, features, scale, exp_id, p_id)
    ori = _construct_orientations_layer(coords, features, scale, exp_id, p_id)

    # invert order for convenience (latest added layer is selected)
    return [ori, pos]


def read_particles(particles):
    """
    Takes a valid poseset and converts it into napari layers.
    """
    layers = []
    for exp_id, features in particles.groupby(PSDL.EXPERIMENT_ID):
        features = features.reset_index(drop=True)

        ndim = 3 if PSDL.POSITION_Z in features else 2
        # order is zyx in napari       ndim = 3 if PSDL.POSITION_Z in features else 2
        coords = invert_xyz(np.asarray(features[PSDL.POSITION[:ndim]]))
        shifts = invert_xyz(np.asarray(features[PSDL.SHIFT[:ndim]]))
        coords += shifts
        px_size = features[PSDL.PIXEL_SPACING].iloc[0]
        if not px_size:
            warnings.warn("unknown pixel spacing, setting to 1 Angstrom")
            px_size = 1

        layers.extend(
            construct_particle_layer_tuples(coords, features, px_size, exp_id)
        )

    return layers


def read_image(image):
    px_size = image.pixel_spacing
    if not px_size:
        warnings.warn("unknown pixel spacing, setting to 1 Angstrom")
        px_size = 1
    return (
        image.data,
        dict(
            name=f"{image.experiment_id} - image",
            scale=[px_size] * image.data.ndim,
            metadata={"experiment_id": image.experiment_id, "stack": image.stack},
            interpolation2d="spline36",
            interpolation3d="linear",
            rendering="average",
            depiction="plane",
            blending="translucent",
            plane=dict(thickness=5),
        ),
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
        dict(
            name=f"{exp_id} - surface lines",
            edge_width=50 / scale[0],
            metadata={"experiment_id": exp_id},
            scale=scale,
            features={"surface_id": surf_id},
            feature_defaults={"surface_id": surf_id.max() + 1},
            edge_color_cycle=edge_color_cycle,
            edge_color="surface_id",
            shape_type="path",
            ndim=3,
        ),
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
        dict(
            name=f"{exp_id} - surface",
            metadata={"experiment_id": exp_id},
            shading="smooth",
            scale=scale,
            # TODO: needs to exposed in napari
            # colormap=colormap
        ),
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

    data_list = read(*cryohub_paths, **kwargs)
    # sort so we get images first, better for some visualization circumstances
    for data in sorted(data_list, key=lambda x: not isinstance(x, Image)):
        if isinstance(data, Image):
            layers.append(read_image(data))
        elif isinstance(data, PoseSet):
            layers.extend(read_particles(data))

    for lay in layers:
        lay[1]["visible"] = False  # speed up loading
    return layers or None
