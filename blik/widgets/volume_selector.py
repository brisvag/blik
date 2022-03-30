from magicgui import magic_factory
from typing import TYPE_CHECKING
from napari.utils._magicgui import find_viewer_ancestor

if TYPE_CHECKING:
    import napari


def _get_choices(wdg):
    """
    generate choices for the volume dropdown based on the layers in the layerlist
    """
    viewer = find_viewer_ancestor(wdg.native)
    if not viewer:
        return []

    choices = set()
    for lay in viewer.layers:
        try:
            vol = lay.metadata['blik_volume']
        except KeyError:
            continue
        if vol is not None:
            choices.add(vol)
    return sorted(list(choices))


def _on_init(wdg):
    """
    hook up widget to update choices wheneven things change in the layerlist

    also sets up a few things on the viewer
    """
    @wdg.parent_changed.connect
    def _look_for_viewer():
        viewer = find_viewer_ancestor(wdg.native)
        if viewer:
            viewer.layers.events.inserted.connect(wdg.volume.reset_choices)
            viewer.layers.events.removed.connect(wdg.volume.reset_choices)

            viewer.scale_bar.unit = '0.1nm'  # pixels are 1 Angstrom
            viewer.scale_bar.visible = True


@magic_factory(
    auto_call=True,
    call_button=False,
    widget_init=_on_init,
    volume=dict(widget_type='ComboBox', choices=_get_choices, nullable=True),
)
def volume_selector(viewer: 'napari.Viewer', volume):
    """
    Select which volume to display in napari and hide everything else.
    """
    sel = []
    if viewer is None:
        return
    for layer in viewer.layers:
        try:
            layer_vol = layer.metadata['blik_volume']
        except KeyError:
            # leave untracked layers alone, and keep them in the selection if there
            if layer in viewer.selection:
                sel.append(layer)
            continue
        if layer_vol == volume:
            layer.visible = True
            sel.append(layer)
        else:
            layer.visible = False
    viewer.layers.selection = set(sel)
