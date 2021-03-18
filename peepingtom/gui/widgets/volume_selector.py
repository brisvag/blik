from qtpy.QtWidgets import QVBoxLayout, QWidget, QComboBox, QLabel


class VolumeSelector:
    name = 'PeepingTom - Volume Selector'

    def __init__(self, viewer):
        self.viewer = viewer
        self._selected = None

        self._init_gui()

        if self.volumes:
            self.select_from_dropdown()

    def _init_gui(self):
        self.widget = QWidget()
        layout = QVBoxLayout()
        self.widget.setLayout(layout)

        layout.addWidget(QLabel(self.name))

        self.dropdown = QComboBox(self.widget)
        self.dropdown.addItems(self.volumes.keys())
        self.dropdown.currentIndexChanged.connect(self.select_from_dropdown)
        layout.addWidget(self.dropdown)

    @property
    def volumes(self):
        return self.viewer.peeper.volumes

    @property
    def selected(self):
        if self._selected is not None:
            return self.volumes[self._selected]
        return []

    def select(self, volume):
        if volume not in self.volumes:
            raise KeyError(f'{volume} is not in volumes')
        self._selected = volume
        self.show_selected()

    def select_from_dropdown(self, i=None):
        self.select(self.dropdown.currentText())

    @property
    def selected_layers(self):
        layers = []
        for db in self.selected:
            for dep in db.depictors:
                layers.extend(getattr(dep, 'layers', []))
        return layers

    def show_selected(self, **kwargs):
        for db in self.selected:
            db.depict(**kwargs)
        self.viewer.napari_viewer.layers.clear()
        self.viewer.napari_viewer.layers.extend(self.selected_layers)
