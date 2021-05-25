from peepingtom.peeper import Peeper
from peepingtom.datablocks import PointBlock


def test_napari(make_napari_viewer):
    p = Peeper(PointBlock(data=[[0, 0, 0]]))
    viewer = make_napari_viewer(strict_qt=False)
    p.show(napari_viewer=viewer)
    p.viewer.toggle_plots()
    p.purge_gui()
