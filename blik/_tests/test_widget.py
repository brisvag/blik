import napari
import numpy as np
import mrcfile

from blik.widgets.main_widget import MainBlikWidget
from blik.widgets.file_reader import file_reader
from blik.widgets.filter import bandpass_filter, gaussian_filter


def test_main_widget(make_napari_viewer):
    wdg = MainBlikWidget()
    assert 'test' not in wdg[0].experiment_id.choices

    viewer = make_napari_viewer()
    with napari.layers._source.layer_source(reader_plugin='blik'):
        viewer.add_points(metadata={'experiment_id': 'test'})
    viewer.window.add_dock_widget(wdg)
    assert 'test' in wdg[0].experiment_id.choices


def test_reader_widget(make_napari_viewer, star_file):
    viewer = make_napari_viewer()
    wdg = file_reader()
    viewer.window.add_dock_widget(wdg)
    wdg.files.value = [star_file]
    wdg.name_regex.value = [r'\w']

    assert len(viewer.layers) == 0
    wdg()
    assert len(viewer.layers) == 2


def test_gaussian_filter_widget(make_napari_viewer, mrc_file):
    viewer = make_napari_viewer()
    wdg = gaussian_filter()
    viewer.window.add_dock_widget(wdg)
    with mrcfile.open(mrc_file) as mrc:
        layer = viewer.add_image(mrc.data, metadata={'experiment_id': 'test', 'stack': False})
    assert wdg.image.value == layer
    wdg()
    result = viewer.layers[-1].data
    assert np.all(result != 1)


def test_bandpass_filter_widget(make_napari_viewer, mrc_file):
    viewer = make_napari_viewer()
    wdg = bandpass_filter()
    viewer.window.add_dock_widget(wdg)
    with mrcfile.open(mrc_file) as mrc:
        layer = viewer.add_image(mrc.data, metadata={'experiment_id': 'test', 'stack': False})
    assert wdg.image.value == layer
    wdg()
    result = viewer.layers[-1].data
    assert np.all(result != 1)
