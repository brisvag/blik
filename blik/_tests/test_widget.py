import napari
import numpy as np

from blik.widgets.volume_selector import volume_selector
from blik.widgets.file_reader import file_reader
from blik.widgets.filter import bandpass_filter, gaussian_filter


def test_volume_widget(make_napari_viewer):
    viewer = make_napari_viewer()

    with napari.layers._source.layer_source(reader_plugin='blik'):
        viewer.add_points(metadata={'blik_volume': 'test'})

    wdg = volume_selector()
    assert 'test' not in wdg.volume.choices
    viewer.window.add_dock_widget(wdg)
    assert 'test' in wdg.volume.choices


def test_reader_widget(make_napari_viewer, star_file):
    viewer = make_napari_viewer()
    wdg = file_reader()
    viewer.window.add_dock_widget(wdg)
    wdg.files.value = [star_file]
    wdg.name_regex.value = [r'\w']

    assert len(viewer.layers) == 0
    wdg()
    assert len(viewer.layers) == 8


def test_gaussian_filter_widget(make_napari_viewer, mrc_file):
    viewer = make_napari_viewer()
    wdg = gaussian_filter()
    viewer.window.add_dock_widget(wdg)
    layer = viewer.open(mrc_file)[0]
    assert wdg.image.value == layer
    wdg()
    result = viewer.layers[-1].data
    assert np.all(result != 1)


def test_bandpass_filter_widget(make_napari_viewer, mrc_file):
    viewer = make_napari_viewer()
    wdg = bandpass_filter()
    viewer.window.add_dock_widget(wdg)
    layer = viewer.open(mrc_file)[0]
    assert wdg.image.value == layer
    wdg()
    result = viewer.layers[-1].data
    assert np.all(result != 1)
