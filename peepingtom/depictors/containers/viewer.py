import napari
from pyqtgraph import GraphicsLayoutWidget


class Viewer:
    def __init__(self, napari_viewer=None, plots_widget=None):
        self.napari_viewer = None
        self.plots = None
        self._plots_napari_widget = None
        self._init_viewer(napari_viewer)
        self._init_plots(plots_widget)

    def _init_viewer(self, napari_viewer=None):
        if napari_viewer is None:
            napari_viewer = napari.Viewer(ndisplay=3)
        self.napari_viewer = napari_viewer
        self._check()

    def _init_plots(self, plots_widget=None):
        self._check()
        if plots_widget is None:
            plots_widget = GraphicsLayoutWidget()
        self.plots = plots_widget
        self._plots_napari_widget = self.napari_viewer.window.add_dock_widget(self.plots)
        # use napari hide and show methods
        self.plots.show = self._plots_napari_widget.show
        self.plots.hide = self._plots_napari_widget.hide
        self.plots.hide()

    def _check(self):
        try:
            self.napari_viewer.window.qt_viewer.actions()
        except RuntimeError:
            self._init_viewer()
            self._init_plots()

    @property
    def layers(self):
        return self.napari_viewer.layers
