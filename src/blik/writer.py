import numpy as np
from cryohub.utils.generic import get_columns_or_default
from cryohub.utils.types import PoseSet
from cryohub.writing.mrc import write_mrc
from cryohub.writing.star import write_star
from cryohub.writing.tbl import write_tbl
from cryotypes.image import Image
from scipy.spatial.transform import Rotation

from .utils import invert_xyz


def write_image(path, data, attributes):
    if "experiment_id" not in attributes["metadata"]:
        raise ValueError(
            "cannot write a layer that does not have blik metadata. Add it to an experiment!"
        )
    img = Image(
        data=data,
        experiment_id=attributes["metadata"]["experiment_id"],
        pixel_spacing=attributes["scale"][0],
        stack=attributes["metadata"].get("stack", False),
        source=attributes["metadata"].get("source", ""),
    )
    write_mrc(img, str(path), overwrite=True)
    return [path]


def _generate_particle_set(layer_data):
    particles = []
    for data, attributes, layer_type in layer_data:
        if layer_type == "vectors":
            # vector info is actually held in particles, but this makes it
            # convenient to select everything and save
            pass
        elif "experiment_id" in attributes["metadata"]:
            data = invert_xyz(data)
            shift_cols = ["shift_z", "shift_y", "shift_x"]
            features = attributes["features"].drop(
                columns=["orientation", *shift_cols], errors="ignore"
            )

            shift = get_columns_or_default(attributes["features"], shift_cols)
            if shift is not None:
                shift = invert_xyz(shift)
                data = data - shift
            ori = get_columns_or_default(attributes["features"], "orientation")
            if ori is not None:
                ori = Rotation.concatenate(ori.reshape(-1))

            particles.append(
                PoseSet(
                    position=data,
                    shift=shift,
                    orientation=ori,
                    experiment_id=attributes["metadata"]["experiment_id"],
                    pixel_spacing=attributes["scale"][0],
                    source=attributes["metadata"].get("source", ""),
                    features=features,
                )
            )
        else:
            raise ValueError(
                "cannot write a layer that does not have blik metadata. Add it to an experiment!"
            )
    return particles


def _write_particles_star(path, layer_data, relion_version):
    particles = _generate_particle_set(layer_data)
    write_star(particles, path, overwrite=True, version=relion_version)
    return [path]


def write_particles_relion_30(path, layer_data):
    return _write_particles_star(path, layer_data, relion_version="3.0")


def write_particles_relion_31(path, layer_data):
    return _write_particles_star(path, layer_data, relion_version="3.1")


def write_particles_relion_40(path, layer_data):
    return _write_particles_star(path, layer_data, relion_version="4.0")


def write_particles_dynamo(path, layer_data):
    particles = _generate_particle_set(layer_data)
    write_tbl(particles, path, overwrite=True)
    return [path]


def write_surface_picks(path, data, attributes):
    if "experiment_id" not in attributes["metadata"]:
        raise ValueError(
            "cannot write a layer that does not have blik metadata. Add it to an experiment!"
        )

    if not str(path).endswith(".picks"):
        path = str(path) + ".picks"

    exp_id = str(attributes["metadata"]["experiment_id"])
    scale = attributes["scale"]
    surf_id = attributes["features"]["surface_id"]
    edge_color_cycle = attributes["edge_color_cycle"]
    with open(path, "wb") as f:
        np.save(f, scale)
        np.save(f, surf_id)
        np.save(f, edge_color_cycle)
        for line in data:
            np.save(f, line)
        # exp ID at the end cause it has variable length and is not a np array
        f.write(exp_id.encode())
    return [path]


def write_surface(path, data, attributes):
    if "experiment_id" not in attributes["metadata"]:
        raise ValueError(
            "cannot write a layer that does not have blik metadata. Add it to an experiment!"
        )

    if not str(path).endswith(".surf"):
        path = str(path) + ".surf"

    exp_id = str(attributes["metadata"]["experiment_id"])
    scale = attributes["scale"]
    # TODO: needs to exposed in napari
    # colormap = attributes['colormap']['colors']
    with open(path, "wb") as f:
        np.save(f, scale)
        # TODO: needs to exposed in napari
        # np.save(f, colormap)
        for d in data:
            np.save(f, d)
        # exp ID at the end cause it has variable length and is not a np array
        f.write(exp_id.encode())
    return [path]
