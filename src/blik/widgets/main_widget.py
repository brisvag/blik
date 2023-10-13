from __future__ import annotations

from typing import List

import napari
import numpy as np
import pandas as pd
from magicgui import magic_factory, magicgui
from magicgui.widgets import Container
from napari.layers import Image, Labels, Points, Shapes, Vectors
from napari.utils._magicgui import find_viewer_ancestor
from napari.utils.notifications import show_info
from scipy.spatial.transform import Rotation

from ..reader import construct_particle_layer_tuples
from ..utils import generate_vectors, invert_xyz, layer_tuples_to_layers
from .picking import (
    _generate_filaments_from_points_layer,
    _generate_surface_grids_from_shapes_layer,
    _resample_filament,
    _resample_surfaces,
)


def _get_choices(wdg, condition=None):
    """generate choices for the experiment_id dropdown based on the layers in the layerlist."""
    viewer = find_viewer_ancestor(wdg.native)
    if not viewer:
        return []

    choices = set()
    for lay in viewer.layers:
        if condition is not None and not condition(lay):
            continue
        try:
            exp = lay.metadata["experiment_id"]
        except KeyError:
            continue
        if exp is not None:
            choices.add(exp)
    return sorted(choices)


def _connect_points_to_vectors(p, v):
    """connect a particle points layer to a vectors layer to keep them in sync."""

    def _update_vectors():
        if not len(p.data):
            return
        if np.any(pd.isnull(p.features["orientation"])):
            obj = p.features["orientation"].astype(object)
            obj[pd.isnull(obj)] = Rotation.identity()
            p.features["orientation"] = obj
        vec_data, vec_color = generate_vectors(p.data[...], p.features["orientation"])
        v.data = vec_data
        v.edge_color = vec_color

    p.events.set_data.disconnect(_update_vectors)
    p.events.set_data.connect(_update_vectors)
    p.events.features.disconnect(_update_vectors)
    p.events.features.connect(_update_vectors)


def _connect_picking_callbacks(surf):
    @surf.bind_key("n", overwrite=True)
    def next_surface(ev):
        surf.feature_defaults["surface_id"] += 1

    @surf.bind_key("p", overwrite=True)
    def previous_surface(ev):
        surf.feature_defaults["surface_id"] -= 1


def _attach_callbacks_to_viewer(wdg):
    """attach all callbacks to the napari viewer and enable scale bar."""
    viewer = find_viewer_ancestor(wdg.native)
    if viewer:
        viewer.layers.events.inserted.connect(lambda e: _connect_layers(viewer, e))
        _connect_layers(viewer, None)

        viewer.scale_bar.unit = "0.1nm"  # pixels are 1 A
        viewer.scale_bar.visible = True


def _connect_layers(viewer, e):
    """connect all points and vectors layers with the necessary callbacks."""
    points = {}
    vectors = {}
    for lay in viewer.layers:
        if "experiment_id" not in lay.metadata:
            continue

        p_id = lay.metadata.get("p_id", None)
        if p_id is not None:
            if isinstance(lay, Points):
                points[p_id] = lay
            elif isinstance(lay, Vectors):
                vectors[p_id] = lay
        if isinstance(lay, Shapes):
            _connect_picking_callbacks(lay)

    for p_id, p in points.items():
        v = vectors.get(p_id, None)
        if v is not None:
            _connect_points_to_vectors(p, v)


@magic_factory(
    auto_call=True,
    call_button=False,
    labels=False,
    experiment_id={
        "widget_type": "ComboBox",
        "choices": _get_choices,
        "nullable": True,
    },
)
def experiment(viewer: napari.Viewer, experiment_id):
    """Select which experiment_id to display in napari and hide everything else."""
    sel = []
    if viewer is None:
        return
    for layer in viewer.layers:
        try:
            layer_exp = layer.metadata["experiment_id"]
        except KeyError:
            # leave untracked layers alone, and keep them in the selection if there
            if layer in viewer.layers.selection:
                sel.append(layer)
            continue
        if layer_exp == experiment_id:
            layer.visible = True
            sel.append(layer)
        else:
            layer.visible = False
    viewer.layers.selection = set(sel)
    experiment.current_layers = set(sel)


@magicgui(
    labels=False,
    call_button="Add",
)
def add_to_exp(layer: napari.layers.Layer):
    """add layer to the current experiment."""
    layer.metadata["experiment_id"] = add_to_exp._main_widget[
        "experiment"
    ].experiment_id.value
    if isinstance(layer, (Image, Labels)):
        if "stack" not in layer.metadata:
            layer.metadata["stack"] = False


@magicgui(
    labels=False,
    call_button="Create",
    l_type={
        "choices": ["segmentation", "particles", "surface_picking", "filament_picking"]
    },
)
def new(
    l_type,
) -> List[napari.layers.Layer]:  # noqa. This must be List, not list (magicgui...)
    """create a new layer to add to this experiment."""
    layers = getattr(new._main_widget["experiment"], "current_layers", [])
    if not layers:
        show_info("no experiment is selected")
        return []

    exp_id = new._main_widget["experiment"].experiment_id.value
    if l_type == "segmentation":
        for lay in layers:
            if isinstance(lay, Image) and lay.metadata["experiment_id"] == exp_id:
                labels = Labels(
                    np.zeros(lay.data.shape, dtype=np.int32),
                    name=f"{exp_id} - segmentation",
                    scale=lay.scale,
                    metadata={
                        "experiment_id": exp_id,
                        "stack": lay.metadata["stack"],
                    },
                )
                return [labels]
    elif l_type == "particles":
        for lay in layers:
            if lay.metadata["experiment_id"] == exp_id:
                layers = construct_particle_layer_tuples(
                    coords=None, features=None, scale=lay.scale[0], exp_id=exp_id
                )
                return layer_tuples_to_layers(layers)
    elif l_type == "surface_picking":
        for lay in layers:
            if isinstance(lay, Image) and lay.metadata["experiment_id"] == exp_id:
                pts = Shapes(
                    name=f"{exp_id} - surface lines",
                    edge_width=50 / lay.scale[0],
                    scale=lay.scale,
                    metadata={"experiment_id": exp_id},
                    features={"surface_id": np.empty(0, int)},
                    feature_defaults={"surface_id": 0},
                    edge_color_cycle=np.random.rand(30, 3),
                    edge_color="surface_id",
                    ndim=3,
                )

                return [pts]
    elif l_type == "filament_picking":
        for lay in layers:
            if isinstance(lay, Image) and lay.metadata["experiment_id"] == exp_id:
                pts = Points(
                    name=f"{exp_id} - filament picks",
                    size=100 / lay.scale[0],
                    scale=lay.scale,
                    metadata={"experiment_id": exp_id},
                    face_color_cycle=np.random.rand(30, 3),
                    ndim=3,
                )

                return [pts]

    show_info(f"cannot create a new {l_type}")
    return []


@magicgui(
    labels=True,
    call_button="Generate",
    spacing_A={"widget_type": "Slider", "min": 1, "max": 500},
    inside_points={"nullable": True},
)
def surface(
    surface_shapes: napari.layers.Shapes,
    inside_points: napari.layers.Points,
    spacing_A=100,
    closed=False,
) -> napari.types.LayerDataTuple:
    """create a new surface representation from picked surface points."""
    surface_grids, colors = _generate_surface_grids_from_shapes_layer(
        surface_shapes, spacing_A
    )

    meshes = []
    exp_id = surface_shapes.metadata["experiment_id"]

    for surf in surface_grids:
        meshes.append(surf.mesh())

    offset = 0
    vert = []
    faces = []
    ids = []
    for surf_id, (v, f) in enumerate(meshes):
        f += offset
        offset += len(v)
        vert.append(v)
        faces.append(f)
        ids.append(np.full(len(v), surf_id))
    vert = np.concatenate(vert)
    faces = np.concatenate(faces)
    uniq_colors, idx = np.unique(colors, axis=0, return_index=True)
    colormap = uniq_colors[np.argsort(idx)]
    values = np.concatenate(ids) / len(colormap)
    # special case for colormap with 1 color because blacks get autoadded at index 0
    if colormap.shape[0] == 1:
        values += 1

    surface_layer_tuple = (
        (invert_xyz(vert), faces, values),
        {
            "name": f"{exp_id} - surface",
            "metadata": {
                "experiment_id": exp_id,
                "surface_grids": surface_grids,
                "surface_colors": colors,
            },
            "scale": surface_shapes.scale,
            "shading": "smooth",
            "colormap": colormap,
        },
        "surface",
    )
    return [surface_layer_tuple]


@magicgui(
    labels=True,
    call_button="Generate",
    spacing_A={"widget_type": "Slider", "min": 1, "max": 500},
)
def surface_particles(
    surface: napari.layers.Surface,
    spacing_A=50,
) -> napari.types.LayerDataTuple:
    surface_grids = surface.metadata.get("surface_grids", None)
    if surface_grids is None:
        raise ValueError("This surface layer contains no surface grid object.")
    colors = surface.metadata.get("surface_colors")

    exp_id = surface.metadata["experiment_id"]
    spacing = spacing_A / surface.scale[0]

    pos = []
    ori = []
    for surf in surface_grids:
        if not np.isclose(surf.separation, spacing):
            surf.separation = spacing
        pos.append(surf.sample())
        ori.append(surf.sample_orientations())

    pos = np.concatenate(pos)
    features = pd.DataFrame({"orientation": np.asarray(Rotation.concatenate(ori))})

    vec_layer_tuple, pos_layer_tuple = construct_particle_layer_tuples(
        coords=invert_xyz(pos),
        features=features,
        scale=surface.scale[0],
        exp_id=exp_id,
        face_color_cycle=colors,
    )
    return [vec_layer_tuple, pos_layer_tuple]


@magicgui(
    labels=True,
    call_button="Resample",
    spacing_A={"widget_type": "Slider", "min": 1, "max": 500},
    thickness_A={"widget_type": "Slider", "min": 1, "max": 500},
)
def resample_surface(
    surface: napari.layers.Surface,
    volume: napari.layers.Image,
    spacing_A=5,
    thickness_A=200,
    masked=False,
) -> napari.types.LayerDataTuple:
    surface_grids = surface.metadata.get("surface_grids", None)
    if surface_grids is None:
        raise ValueError("This surface layer contains no surface grid object.")

    exp_id = surface.metadata["experiment_id"]
    spacing = spacing_A / surface.scale[0]
    thickness = int(np.round(thickness_A / surface.scale[0]))
    for surf in surface_grids:
        if not np.isclose(surf.separation, spacing):
            surf.separation = spacing

    vols = _resample_surfaces(volume, surface_grids, spacing, thickness, masked)

    v = napari.Viewer()
    for i, vol in enumerate(vols):
        v.add_image(
            vol,
            name=f"{exp_id} - surface_{i} resampled",
            metadata={"experiment_id": exp_id},
            scale=surface.scale,
        )


@magicgui(
    labels=True,
    call_button="Generate",
)
def filament(
    points: napari.layers.Points,
) -> napari.types.LayerDataTuple:
    filament = _generate_filaments_from_points_layer(points)

    exp_id = points.metadata["experiment_id"]

    path = filament.sample(n_samples=len(points.data) * 50)
    shapes_layer_tuple = (
        [invert_xyz(path)],
        {
            "name": f"{exp_id} - filament",
            "metadata": {
                "experiment_id": exp_id,
                "helical_filament": filament,
            },
            "scale": points.scale,
            "shape_type": "path",
        },
        "shapes",
    )
    return [shapes_layer_tuple]


@magicgui(
    labels=True,
    call_button="Generate",
    rise_A={"widget_type": "Slider", "min": 1, "max": 500},
    radius_A={"widget_type": "Slider", "min": 0, "max": 500},
    twist_deg={"widget_type": "Slider", "min": 0, "max": 360},
    twist_offset={"widget_type": "Slider", "min": 0, "max": 360},
)
def filament_particles(
    filament: napari.layers.Shapes,
    rise_A=50,
    twist_deg=0,
    twist_offset=0,
    radius_A=0,
    cyclic_symmetry_order=1,
) -> napari.types.LayerDataTuple:
    helical_filament = filament.metadata.get("helical_filament", None)
    if helical_filament is None:
        raise ValueError("This shapes layer contains no helical filament object.")

    exp_id = filament.metadata["experiment_id"]

    pos, ori = helical_filament.sample_helical(
        rise=rise_A / filament.scale[0],
        twist=twist_deg,
        radial_offset=radius_A / filament.scale[0],
        cyclic_symmetry_order=cyclic_symmetry_order,
        twist_offset=twist_offset,
        degrees=True,
    )

    features = pd.DataFrame({"orientation": np.asarray(Rotation.concatenate(ori))})

    vec_layer_tuple, pos_layer_tuple = construct_particle_layer_tuples(
        coords=invert_xyz(pos),
        features=features,
        scale=filament.scale[0],
        exp_id=exp_id,
    )
    return [vec_layer_tuple, pos_layer_tuple]


@magicgui(
    labels=True,
    call_button="Resample",
    spacing_A={"widget_type": "Slider", "min": 1, "max": 500},
    thickness_A={"widget_type": "Slider", "min": 1, "max": 500},
)
def resample_filament(
    filament: napari.layers.Shapes,
    volume: napari.layers.Image,
    spacing_A=5,
    thickness_A=200,
) -> napari.types.LayerDataTuple:
    helical_filament = filament.metadata.get("helical_filament", None)
    if helical_filament is None:
        raise ValueError("This shapes layer contains no helical filament object.")

    exp_id = filament.metadata["experiment_id"]
    spacing = spacing_A / filament.scale[0]
    thickness = int(np.round(thickness_A / filament.scale[0]))

    vol = _resample_filament(volume, helical_filament, spacing, thickness)

    v = napari.Viewer()
    v.add_image(
        vol,
        name=f"{exp_id} - filament resampled",
        metadata={"experiment_id": exp_id},
        scale=filament.scale,
    )


class MainBlikWidget(Container):
    """
    Main widget for blik controls.

    Allows to select which layers to view based on the experiment id, to add
    existing layer to a certain experiment id, and to create new analysis layers
    within.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        exp = experiment()
        self.parent_changed.connect(lambda _: _attach_callbacks_to_viewer(exp))
        self.append(exp)
        self.append(new)
        self.append(add_to_exp)
        self.append(surface)
        self.append(surface_particles)
        self.append(resample_surface)
        self.append(filament)
        self.append(filament_particles)
        self.append(resample_filament)
        self.scrollable = True

    def append(self, item):
        super().append(item)
        item._main_widget = self
