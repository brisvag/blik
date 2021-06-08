from peepingtom.peeper import Peeper
from peepingtom.datablocks import PointBlock


def test_viewer(make_napari_viewer):
    p = Peeper(PointBlock(data=[[0, 0, 0]]))
    viewer = make_napari_viewer(strict_qt=False)
    p.show(napari_viewer=viewer)
    p.viewer.toggle_plots()
    p.viewer.update_pt_widget()
    p.viewer.previous_volume()
    p.viewer.next_volume()
    p.purge_gui()
