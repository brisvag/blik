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
        if lay.source.reader_plugin != 'blik':
            continue
        choices.add(lay.metadata['volume'])
    return sorted(list(choices))


def _on_init(wdg):
    """
    hook up widget to update choices wheneven things change in the layerlist
    """
    @wdg.parent_changed.connect
    def _look_for_viewer():
        viewer = find_viewer_ancestor(wdg.native)
        if viewer:
            viewer.layers.events.inserted.connect(wdg.volume.reset_choices)
            viewer.layers.events.removed.connect(wdg.volume.reset_choices)


@magic_factory(
    auto_call=True,
    call_button=False,
    widget_init=_on_init,
    volume=dict(choices=_get_choices),
)
def volume_selector(viewer: 'napari.Viewer', volume):
    """
    Select which volume to display in napari and hide everything else.
    """
    if viewer is None:
        return
    for layer in viewer.layers:
        if layer.metadata['volume'] == volume:
            layer.visible = True
        else:
            layer.visible = False
