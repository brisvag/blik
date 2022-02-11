from magicgui import magic_factory
from typing import TYPE_CHECKING
from napari.utils._magicgui import find_viewer_ancestor

if TYPE_CHECKING:
    import napari


def _get_choices(wdg):
    viewer = find_viewer_ancestor(wdg.native)
    if not viewer:
        return []

    choices = set()
    for lay in viewer.layers:
        if lay.source.reader_plugin != 'blik':
            continue
        choices.add(lay.metadata['volume'])
    return sorted(list(choices))


@magic_factory(
    auto_call=True,
    call_button=False,
    volume=dict(choices=_get_choices),
)
def volume_widget(viewer: 'napari.Viewer', volume):
    if viewer is None:
        return
    for layer in viewer.layers:
        if layer.metadata['volume'] == volume:
            layer.visible = True
        else:
            layer.visible = False
