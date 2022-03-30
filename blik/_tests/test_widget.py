from blik.widgets.volume_selector import volume_selector
import napari


def test_volume_widget(make_napari_viewer):
    viewer = make_napari_viewer()

    with napari.layers._source.layer_source(reader_plugin='blik'):
        viewer.add_points(metadata={'blik_volume': 'test'})

    wdg = volume_selector()
    assert 'test' not in wdg.volume.choices
    viewer.window.add_dock_widget(wdg)
    assert 'test' in wdg.volume.choices
