import numpy as np
from qtpy.QtWidgets import QWidget, QSlider, QComboBox

from ...core import ParticleBlock


class ParticleSelector(QWidget):
    def __init__(self, peeper):
        self.peeper = peeper
        self.widgets = {}

    @property
    def particles(self):
        return self.peeper._get_datablocks(ParticleBlock)

    def add_particle_widget(self, property_name, particles=None):
        if particles is None:
            particles = self.particles
        for part in particles:
            prop = part.properties[property_name]
            if prop.dtype == float:
                widget = QSlider(minimum=prop.min(), maximum=prop.max())
            np.unique()
        widget = None
        self.widgets[property_name] = widget
