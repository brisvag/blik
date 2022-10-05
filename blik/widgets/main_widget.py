from magicgui import magic_factory
from typing import TYPE_CHECKING
from napari.utils._magicgui import find_viewer_ancestor
from napari.layers import Points, Vectors
from cryotypes.poseset import PoseSetDataLabels as PSDL

from ..utils import generate_vectors

if TYPE_CHECKING:
    import napari


def _get_choices(wdg):
    """
    generate choices for the experiment_id dropdown based on the layers in the layerlist
    """
    viewer = find_viewer_ancestor(wdg.native)
    if not viewer:
        return []

    choices = set()
    for lay in viewer.layers:
        try:
            exp = lay.metadata['experiment_id']
        except KeyError:
            continue
        if exp is not None:
            choices.add(exp)
    return sorted(list(choices))


def _connect_points_to_vectors(p, v):
    def _update_vectors():
        vec_data, vec_color = generate_vectors(p.data, p.features[PSDL.ORIENTATION])
        v.data = vec_data
        v.edge_color = vec_color

    def _update_features_from_points():
        with p.events.features.blocker(_update_points_from_features):
            p.features[PSDL.POSITION] = p.data[:, ::-1]

    def _update_points_from_features():
        with p.events.data.blocker(_update_features_from_points):
            p.data[:, ::-1] = p.features[PSDL.POSITION]

    p.events.data.connect(_update_features_from_points)
    p.events.features.connect(_update_points_from_features)
    p.events.data.connect(_update_vectors)
    p.events.features.connect(_update_vectors)


def _on_init(wdg):
    """
    hook up widget to update choices wheneven things change in the layerlist

    also sets up a few things on the viewer
    """
    @wdg.parent_changed.connect
    def _look_for_viewer():
        viewer = find_viewer_ancestor(wdg.native)
        if viewer:
            viewer.layers.events.inserted.connect(wdg.experiment_id.reset_choices)
            viewer.layers.events.removed.connect(wdg.experiment_id.reset_choices)
            viewer.layers.events.inserted.connect(lambda e: _connect_layers(viewer, e))
            _connect_layers(viewer, None)

            viewer.scale_bar.unit = '0.1nm'  # pixels are 1 Angstrom
            viewer.scale_bar.visible = True

    def _connect_layers(viewer, e):
        points = {}
        vectors = {}
        for lay in viewer.layers:
            p_id = lay.metadata.get('p_id', None)
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
    widget_init=_on_init,
    experiment_id=dict(widget_type='ComboBox', choices=_get_choices, nullable=True),
)
def main_widget(viewer: 'napari.Viewer', experiment_id):
    """
    Select which experiment_id to display in napari and hide everything else.
    """
    sel = []
    if viewer is None:
        return
    for layer in viewer.layers:
        try:
            layer_exp = layer.metadata['experiment_id']
        except KeyError:
            # leave untracked layers alone, and keep them in the selection if there
            if layer in viewer.selection:
                sel.append(layer)
            continue
        if layer_exp == experiment_id:
            layer.visible = True
            sel.append(layer)
        else:
            layer.visible = False
    viewer.layers.selection = set(sel)