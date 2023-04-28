import numpy as np
import pandas as pd
from cryohub.writing.mrc import write_mrc
from cryohub.writing.star import write_star
from cryotypes.image import Image
from cryotypes.poseset import validate_poseset_dataframe


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
        source="",
    )
    write_mrc(img, str(path), overwrite=True)
    return [path]


def write_particles(path, layer_data):
    dfs = []
    for data, attributes, layer_type in layer_data:
        if layer_type == "vectors":
            # vector info is actually held in particles, but this makes it
            # convenient to select everything and save
            pass
        elif "experiment_id" in attributes["metadata"]:
            dfs.append(validate_poseset_dataframe(attributes["features"], coerce=True))
        else:
            raise ValueError(
                "cannot write a layer that does not have blik metadata. Add it to an experiment!"
            )

    df = pd.concat(dfs, axis=0, ignore_index=True)
    write_star(df, path, overwrite=True)
    return [path]


def write_surface_picks(path, data, attributes):
    if "experiment_id" not in attributes["metadata"]:
        raise ValueError(
            "cannot write a layer that does not have blik metadata. Add it to an experiment!"
        )

    exp_id = str(attributes["metadata"]["experiment_id"])
    surf_id = attributes["features"]["surface_id"]
    edge_color_cycle = attributes["edge_color_cycle"]
    with open(path, "wb") as f:
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

    exp_id = str(attributes["metadata"]["experiment_id"])
    # TODO: needs to exposed in napari
    # colormap = attributes['colormap']['colors']
    with open(path, "wb") as f:
        # TODO: needs to exposed in napari
        # np.save(f, colormap)
        for d in data:
            np.save(f, d)
        # exp ID at the end cause it has variable length and is not a np array
        f.write(exp_id.encode())
    return [path]
