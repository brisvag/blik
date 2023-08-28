import numpy as np
from scipy.spatial.transform import Rotation
from cryohub.writing.mrc import write_mrc
from cryohub.writing.star import write_star
from cryotypes.image import Image
from cryohub.utils.types import PoseSet
from .utils import invert_xyz


def write_image(path, data, attributes):
    if "experiment_id" not in attributes["metadata"]:
        raise ValueError(
            "cannot write a layer that does not have blik metadata. Add it to an experiment!"
        )
    img = Image(
        data=data,
        experiment_id="",
        pixel_spacing=attributes["scale"][0],
        stack=attributes["metadata"]["stack"],
        source=attributes["metadata"].get("source", ""),
    )
    write_mrc(img, str(path), overwrite=True)
    return [path]


def write_particles(path, layer_data):
    particles = []
    for data, attributes, layer_type in layer_data:
        if layer_type == "vectors":
            # vector info is actually held in particles, but this makes it
            # convenient to select everything and save
            pass
        elif "experiment_id" in attributes["metadata"]:
            shift_cols = ['shift_z', 'shift_y', 'shift_x']
            shift = attributes["features"][shift_cols].to_numpy()
            ori = Rotation.concatenate(attributes["features"]["orientation"])
            features = attributes["features"].drop(columns=["orientation", *shift_cols])
            breakpoint()
            particles.append(
                PoseSet(
                    position=invert_xyz(data - shift),
                    shift=invert_xyz(shift),
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

    write_star(particles, path, overwrite=True)
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
