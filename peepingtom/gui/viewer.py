import napari
from pyqtgraph import GraphicsLayoutWidget
from qtpy.QtWidgets import QVBoxLayout, QWidget, QComboBox, QPushButton


class Viewer:
    """
    abstraction layer on viewer that dispatches visualisation to specific components
    and implements widgets for Peeper functionality
    """
    def __init__(self, peeper):
        self.peeper = peeper

        self.napari_viewer = None
        self.plots = None
        self.pt_widget = None

    def show(self, napari_viewer=None, **kwargs):
        self.ensure_ready(napari_viewer=napari_viewer)
        for db in self.peeper:
            db.init_depictor(**kwargs)
        if self.peeper.volumes:
            self.show_volume(list(self.peeper.volumes.keys())[0])
        if self.peeper.plots:
            self.plots.show()

    def ensure_ready(self, napari_viewer=None):
        if napari_viewer is not None:
            self._init_viewer(napari_viewer)
            self._init_plots()
            self._init_pt_widget()
        # check if viewer exists and is still open
        try:
            self.napari_viewer.window.qt_viewer.actions()
        except (AttributeError, RuntimeError):
            self._init_viewer()
            self._init_plots()
            self._init_pt_widget()

    def _init_viewer(self, napari_viewer=None):
        if napari_viewer is not None:
            self.napari_viewer = napari_viewer
        else:
            self.napari_viewer = napari.Viewer(ndisplay=3, title='napari - PeepingTom')
        self.napari_viewer.scale_bar.unit = '0.1nm'
        self.napari_viewer.scale_bar.visible = True
        # TODO: workaround until layer issues are fixed (napari #2110)
        self.napari_viewer.window.qt_viewer.destroyed.connect(self.peeper.purge_gui)

    def _init_plots(self):
        self.plots = GraphicsLayoutWidget()
        self._plots_napari_widget = self.napari_viewer.window.add_dock_widget(self.plots,
                                                                              name='PeepingTom - Plots',
                                                                              area='bottom')
        # use napari hide and show methods
        self.plots.show = self._plots_napari_widget.show
        self.plots.hide = self._plots_napari_widget.hide
        self.plots.hide()

    def _init_pt_widget(self):
        self.pt_widget = QWidget()
        layout = QVBoxLayout()
        self.pt_widget.setLayout(layout)

        self.volume_selector = QComboBox(self.pt_widget)
        self.volume_selector.addItems(self.peeper.volumes.keys())
        self.volume_selector.currentTextChanged.connect(self.show_volume)
        layout.addWidget(self.volume_selector)

        self.plots_toggler = QPushButton('Show / Hide Plots')
        self.plots_toggler.clicked.connect(self.toggle_plots)
        layout.addWidget(self.plots_toggler)

        self._pt_napari_widget = self.napari_viewer.window.add_dock_widget(self.pt_widget,
                                                                           name='PeepingTom - Viewer',
                                                                           area='left')
        # use napari hide and show methods
        self.pt_widget.show = self._pt_napari_widget.show
        self.pt_widget.hide = self._pt_napari_widget.hide

    def show_volume(self, volume):
        if volume is None:
            return
        self.volume_selector.setCurrentText(volume)
        datablocks = self.peeper.omni + self.peeper.volumes[volume]

        layers = []
        plots = []
        for db in datablocks:
            for dep in db.depictors:
                if hasattr(dep, 'layers'):
                    if not dep.layers:
                        dep.depict()
                    layers.extend(dep.layers)
                elif hasattr(dep, 'plot'):
                    if not dep.plot.curves:
                        dep.depict()
                    plots.append(dep.plot)
        layers = sorted(layers, key=lambda l: isinstance(l, napari.layers.Image), reverse=True)

        self.napari_viewer.layers.clear()
        self.napari_viewer.layers.extend(layers)

        self.plots.clear()
        for plt in plots:
            self.plots.addItem(plt)

    def toggle_plots(self):
        if self.plots.isVisible():
            self.plots.hide()
        else:
            self.plots.show()
