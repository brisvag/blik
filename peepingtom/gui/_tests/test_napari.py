from peepingtom.peeper import Peeper


def test_napari(make_napari_viewer):
    p = Peeper()
    viewer = make_napari_viewer(strict_qt=False)
    p.show(napari_viewer=viewer)
    p.purge_gui()
