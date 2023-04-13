from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
from cryotypes.poseset import PoseSetDataLabels as PSDL
from cryotypes.poseset import validate_poseset_dataframe
from magicgui import magic_factory, magicgui
from magicgui.widgets import Container
from morphosamplers.surface_spline import GriddedSplineSurface
from napari.layers import Image, Labels, Points, Surface, Vectors
from napari.utils._magicgui import find_viewer_ancestor
from napari.utils.notifications import show_info
from scipy.spatial.transform import Rotation

from ..reader import construct_particle_layer_tuples
from ..utils import generate_vectors, invert_xyz, layer_tuples_to_layers

if TYPE_CHECKING:
    import typing

    import napari


def _get_choices(wdg, condition=None):
    """
    generate choices for the experiment_id dropdown based on the layers in the layerlist
    """
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
    return sorted(list(choices))


def _connect_points_to_vectors(p, v):
    """
    connect a particle points layer to a vectors layer to keep them in sync.
    """

    def _update_vectors():
        vec_data, vec_color = generate_vectors(
            p.data[...], p.features[PSDL.ORIENTATION]
        )
        v.data = vec_data
        v.edge_color = vec_color

    def _update_features_from_points():
        with p.events.features.blocker(_update_points_from_features):
            p.features[PSDL.POSITION] = invert_xyz(p.data)
            p.features = validate_poseset_dataframe(p.features, coerce=True)

    def _update_points_from_features():
        with p.events.data.blocker(_update_features_from_points):
            p.data = invert_xyz(p.features[PSDL.POSITION].to_numpy())

    p.events.data.connect(_update_features_from_points)
    p.events.features.connect(_update_points_from_features)
    p.events.features.connect(_update_vectors)

    # set defaults for features, otherwise the callbacks above will fail on new points
    defaults = validate_poseset_dataframe(
        pd.DataFrame(
            {
                PSDL.EXPERIMENT_ID: p.metadata["experiment_id"],
                PSDL.SOURCE: None,
                PSDL.PIXEL_SPACING: p.scale[0],
            },
            index=[0],
        ),
        coerce=True,
    )
    p.feature_defaults[defaults.columns] = defaults


def _attach_callbacks_to_viewer(wdg):
    """
    attach all callbacks to the napari viewer and enable scale bar
    """
    viewer = find_viewer_ancestor(wdg.native)
    if viewer:
        viewer.layers.events.inserted.connect(lambda e: _connect_layers(viewer, e))
        _connect_layers(viewer, None)

        viewer.scale_bar.unit = "0.1nm"  # pixels are 1 Angstrom
        viewer.scale_bar.visible = True


def _connect_layers(viewer, e):
    """
    connect all points and vectors layers with the necessary callbacks
    """
    points = {}
    vectors = {}
    for lay in viewer.layers:
        p_id = lay.metadata.get("p_id", None)
        if p_id is not None:
            if isinstance(lay, Points):
                points[p_id] = lay
            elif isinstance(lay, Vectors):
                vectors[p_id] = lay
    for p_id, p in points.items():
        v = vectors.get(p_id, None)
        if v is not None:
            _connect_points_to_vectors(p, v)


@magic_factory(
    auto_call=True,
    call_button=False,
    labels=False,
    experiment_id=dict(widget_type="ComboBox", choices=_get_choices, nullable=True),
)
def experiment(viewer: napari.Viewer, experiment_id):
    """
    Select which experiment_id to display in napari and hide everything else.
    """
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
    """
    add layer to the current experiment
    """
    layer.metadata["experiment_id"] = add_to_exp._main_widget[
        "experiment"
    ].experiment_id.value
    if isinstance(layer, (Image, Labels)):
        if "stack" not in layer.metadata:
            layer.metadata["stack"] = False


@magicgui(
    labels=False,
    call_button="Create",
    l_type=dict(choices=["segmentation", "particles", "surface_picking"]),
)
def new(l_type) -> typing.List[napari.layers.Layer]:
    """
    create a new layer to add to this experiment
    """
    layers = getattr(new._main_widget["experiment"], "current_layers", [])
    if not layers:
        show_info("no experiment is selected")
        return

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
                features = validate_poseset_dataframe(pd.DataFrame(), coerce=True)
                layers = construct_particle_layer_tuples(
                    None, features, lay.scale, exp_id
                )
                return layer_tuples_to_layers(layers)
    elif l_type == "surface_picking":
        for lay in layers:
            if isinstance(lay, Image) and lay.metadata["experiment_id"] == exp_id:
                pts = Points(
                    name=f"{exp_id} - surface points",
                    scale=lay.scale,
                    size=10 * lay.scale[0],
                    metadata={"experiment_id": exp_id},
                    features={"surface_id": np.empty(0, int)},
                    feature_defaults={"surface_id": 0},
                    face_color_cycle=np.random.rand(30, 3),
                    face_color="surface_id",
                    out_of_slice_display=True,
                )

                @pts.bind_key("n")
                def next_surface(ev):
                    pts.feature_defaults["surface_id"] += 1

                @pts.bind_key("p")
                def previous_surface(ev):
                    pts.feature_defaults["surface_id"] -= 1

                return [pts]

    show_info(f"cannot create a new {l_type}")


@magicgui(
    labels=False,
    call_button="Generate",
    spacing=dict(widget_type="Slider", min=1, max=50),
    output=dict(choices=["surface", "particles"]),
)
def surface(
    surface_points: napari.layers.Points, spacing=15, output="surface"
) -> typing.List[napari.layers.Layer]:
    """
    create a new surface representation from picked surface points
    """
    spacing /= surface_points.scale[0]
    pos = []
    ori = []
    meshes = []
    colors = []
    exp_id = surface_points.metadata["experiment_id"]
    for _, surf in surface_points.features.groupby("surface_id"):
        coords = surface_points.data[surf.index]
        # split based on z value
        z_change = np.unique(coords[:, 0], return_index=True)[1]
        z_change = np.sort(z_change)[1:]
        # sort so lines can be added in between at a later point
        lines = np.split(coords, z_change)
        lines = sorted(lines, key=lambda x: x[0, 0])

        try:
            surface_grid = GriddedSplineSurface(
                points=lines, separation=spacing, order=3
            )
        except ValueError:
            continue

        colors.append(surface_points.face_color[surf.index])

        if output == "particles":
            pos.append(surface_grid.sample())
            ori.append(surface_grid.sample_orientations())
        if output == "surface":
            meshes.append(surface_grid.mesh())

    if not colors:
        raise RuntimeError("could not generate surfaces for some reason")

    colors = np.concatenate(colors)

    if output == "particles":
        pos = np.concatenate(pos)
        poseset = pd.DataFrame()
        poseset[PSDL.POSITION] = pos
        poseset[PSDL.ORIENTATION] = np.array(Rotation.concatenate(ori))
        poseset[PSDL.EXPERIMENT_ID] = exp_id
        poseset[PSDL.PIXEL_SPACING] = surface_points.scale[0]

        poseset = validate_poseset_dataframe(poseset, coerce=True)

        vec_layer, pos_layer = layer_tuples_to_layers(
            construct_particle_layer_tuples(
                pos,
                poseset,
                surface_points.scale,
                exp_id,
            )
        )
        pos_layer.face_color = colors
        return vec_layer, pos_layer

    if output == "surface":
        offset = 0
        vert = []
        faces = []
        ids = []
        for id, (v, f) in enumerate(meshes):
            f += offset
            offset += len(v)
            vert.append(v)
            faces.append(f)
            ids.append(np.full(len(v), id))
        vert = np.concatenate(vert)
        faces = np.concatenate(faces)
        uniq_colors, idx = np.unique(colors, axis=0, return_index=True)
        colormap = uniq_colors[np.argsort(idx)]
        values = np.concatenate(ids) / len(colormap)
        # special case for colormap with 1 color because blacks get autoadded at index 0
        if colormap.shape[0] == 1:
            values += 1

        surface_layer = Surface(
            (vert, faces, values),
            scale=surface_points.scale,
            shading="smooth",
            colormap=colormap,
        )
        return [surface_layer]


@magicgui(
    labels=False,
    call_button="Add",
)
def gen(layer: napari.layers.Layer):
    """
    add layer to the current experiment
    """
    layer.metadata["experiment_id"] = add_to_exp._main_widget[
        "experiment"
    ].experiment_id.value


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

    def append(self, item):
        super().append(item)
        item._main_widget = self
