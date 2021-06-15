from blik.dataset import DataSet
from blik.datablocks import PointBlock


def test_viewer(make_napari_viewer):
    dataset = DataSet(PointBlock(data=[[0, 0, 0]]))
    viewer = make_napari_viewer(strict_qt=False)
    dataset.show(napari_viewer=viewer)
    dataset.viewer.toggle_plots()
    dataset.viewer.update_blik_widget()
    dataset.viewer.previous_volume()
    dataset.viewer.next_volume()
    dataset.purge_gui()
