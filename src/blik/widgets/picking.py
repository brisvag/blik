import numpy as np
from morphosamplers.sampler import sample_volume_around_surface
from morphosamplers.surface_spline import GriddedSplineSurface

from ..utils import invert_xyz


def generate_surface_grids_from_shapes_layer(
    surface_shapes, spacing_A=100, closed=False
):
    """create a new surface representation from picked surface points."""
    spacing_A /= surface_shapes.scale[0]
    colors = []
    surface_grids = []
    data_array = np.array(surface_shapes.data, dtype=object)  # helps with indexing
    for _, surf in surface_shapes.features.groupby("surface_id"):
        lines = data_array[surf.index]
        # sort so lines can be added in between at a later point
        # also move to xyz world so math is the same as reader code
        lines = [
            invert_xyz(line).astype(float)
            for line in sorted(lines, key=lambda x: x[0, 0])
        ]

        try:
            surface_grids.append(
                GriddedSplineSurface(
                    points=lines,
                    separation=spacing_A,
                    order=3,
                    closed=closed,
                )
            )
        except ValueError:
            continue

        colors.append(surface_shapes.edge_color[surf.index])

    if not colors:
        raise RuntimeError("could not generate surfaces for some reason")

    colors = np.concatenate(colors)
    return surface_grids, colors


def resample_surfaces(image_layer, surface_grids, thickness_A):
    thickness_A /= image_layer.scale[0]

    volumes = []
    for surf in surface_grids:
        # transpose because zyx to xyz
        vol = sample_volume_around_surface(
            image_layer.data.T,
            surface=surf,
            sampling_thickness=thickness_A,
            sampling_spacing=1,
            interpolation_order=3,
            masked=False,
        )
        volumes.append(vol.T)
    return volumes
