import warnings
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
            scale=scale,
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
            length=50 / scale[0],
            scale=scale,
            metadata={"experiment_id": exp_id, "p_id": p_id},
            out_of_slice_display=True,
        ),
        "vectors",
    )


def construct_particle_layer_tuples(coords, features, scale, exp_id, p_id=None):
    # unique id so we can connect layers safely
    p_id = p_id if p_id is not None else uuid1()

    # divide by scale top keep constant size. TODO: remove after vispy 0.12 which fixes this
    pos = _construct_positions_layer(coords, features, scale, exp_id, p_id)
    ori = _construct_orientations_layer(coords, features, scale, exp_id, p_id)

    # invert order for convenience (latest added layer is selected)
    return [ori, pos]


def read_particles(particles):
    layers = []
    for exp_id, features in particles.groupby(PSDL.EXPERIMENT_ID):
        features = features.reset_index(drop=True)

        ndim = 3 if PSDL.POSITION_Z in features else 2
        coords = invert_xyz(
            np.asarray(features[PSDL.POSITION[:ndim]])
        )  # order is zyx in napari
        shifts = invert_xyz(np.asarray(features[PSDL.SHIFT[:ndim]]))
        coords += shifts
        px_size = features[PSDL.PIXEL_SPACING].iloc[0]
        if not px_size:
            warnings.warn("unknown pixel spacing, setting to 1 Angstrom")
            px_size = 1
        scale = np.repeat(px_size, ndim)

        layers.extend(construct_particle_layer_tuples(coords, features, scale, exp_id))

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


def read_layers(*paths, **kwargs):
    data_list = read(*paths, **kwargs)
    layers = []
    # sort so we get images first, better for some visualization circumstances
    for data in sorted(data_list, key=lambda x: not isinstance(x, Image)):
        if isinstance(data, Image):
            layers.append(read_image(data))
        elif isinstance(data, PoseSet):
            layers.extend(read_particles(data))

    for lay in layers:
        lay[1]["visible"] = False  # speed up loading
    return layers or None
