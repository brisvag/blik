import napari
from pyqtgraph import GraphicsLayoutWidget

from .widgets import VolumeSelector


class Viewer:
    """
    abstraction layer on viewer that dispatches visualisation to specific components
    """
    def __init__(self, peeper, napari_viewer=None):
        self.peeper = peeper
        self.napari_viewer = None

        self.plots = None
        self._plots_napari_dock_widget = None

        self._init_viewer(napari_viewer)
        self._init_plots()

        self.volume_selector = None
        self._volume_selector_napari_dock_widget = None
        self._init_volume_selector()

    def _init_viewer(self, napari_viewer=None):
        if napari_viewer is None:
            napari_viewer = napari.Viewer(ndisplay=3)
        self.napari_viewer = napari_viewer

    def _init_volume_selector(self):
        self.volume_selector = VolumeSelector(self)
        self._volume_selector_napari_widget = self.napari_viewer.window.add_dock_widget(self.volume_selector.widget,
                                                                                        name=self.volume_selector.name,
                                                                                        area='left')
        self.volume_selector.show = self._volume_selector_napari_widget.show
        self.volume_selector.hide = self._volume_selector_napari_widget.hide

    def _init_plots(self, plots_widget=None):
        if plots_widget is None:
            plots_widget = GraphicsLayoutWidget()
        self.plots = plots_widget
        self._plots_napari_widget = self.napari_viewer.window.add_dock_widget(self.plots,
                                                                              name='PeepingTom - Plots',
                                                                              area='bottom')
        # use napari hide and show methods
        self.plots.show = self._plots_napari_widget.show
        self.plots.hide = self._plots_napari_widget.hide
        self.plots.hide()

    def _check(self):
        """
        make sure that the qt viewer was not destroyed
        """
