from contextlib import contextmanager

import napari
from pyqtgraph import GraphicsLayoutWidget
from qtpy.QtWidgets import QVBoxLayout, QWidget, QComboBox, QPushButton


@contextmanager
def block_signals(widget):
    """
    temporarily disable signals
    """
    widget.blockSignals(True)
    yield
    widget.blockSignals(False)


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

    @property
    def shown(self):
        if self.napari_viewer and self.volume_selector:
            return self.peeper.volumes[self.volume_selector.currentText()]
        return None

    def ensure_ready(self, napari_viewer=None):
        if napari_viewer is not None:
            self._init_viewer(napari_viewer)
            self._init_plots()
            self._init_pt_widget()
            self._hook_keybindings()
        # check if viewer exists and is still open
        try:
            self.napari_viewer.window.qt_viewer.actions()
        except (AttributeError, RuntimeError):
            self._init_viewer()
            self._init_plots()
            self._init_pt_widget()
            self._hook_keybindings()

    def _init_viewer(self, napari_viewer=None):
        if napari_viewer is not None:
            self.napari_viewer = napari_viewer
        else:
            self.napari_viewer = napari.Viewer(title='napari - PeepingTom')
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
                                                                           name='PeepingTom',
                                                                           area='left')
        # use napari hide and show methods
        self.pt_widget.show = self._pt_napari_widget.show
        self.pt_widget.hide = self._pt_napari_widget.hide

    def _hook_keybindings(self):
        self.napari_viewer.bind_key('PageUp', self.previous_volume)
        self.napari_viewer.bind_key('PageDown', self.next_volume)

    def update_pt_widget(self):
        if self.pt_widget is not None:
            current_text = self.volume_selector.currentText()
            with block_signals(self.volume_selector):
                self.volume_selector.clear()
                self.volume_selector.addItems(self.peeper.volumes.keys())
                self.volume_selector.setCurrentText(current_text)
        self.show()

    def clear_shown(self):
        for layer in self.napari_viewer.layers.copy():
            if layer in self.peeper.napari_layers:
                self.napari_viewer.layers.remove(layer)
        self.plots.clear()

    def show_volume(self, volume):
        if volume is None:
            return
        self.volume_selector.setCurrentText(volume)
        datablocks = self.peeper.omni + self.peeper.volumes[volume]
        ndim = 2
        for db in datablocks:
            ndim = max(ndim, getattr(db, 'ndim', 2))
        self.napari_viewer.dims.ndisplay = ndim

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

        self.clear_shown()
        self.napari_viewer.layers.extend(layers)
        for plt in plots:
            self.plots.addItem(plt)

    def previous_volume(self, viewer=None):
        idx = self.volume_selector.currentIndex()
        previous_idx = (idx - 1) % self.volume_selector.count()
        self.volume_selector.setCurrentIndex(previous_idx)

    def next_volume(self, viewer=None):
        idx = self.volume_selector.currentIndex()
        next_idx = (idx + 1) % self.volume_selector.count()
        self.volume_selector.setCurrentIndex(next_idx)

    def toggle_plots(self):
        if self.plots.isVisible():
            self.plots.hide()
        else:
            self.plots.show()
