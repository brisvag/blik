import numpy as np
from numpy.testing import assert_array_almost_equal

from ntp.models import FilamentModel
from ntp.geometric_primitives import Line


# Create a FilamentModel class for testing
class TestFilamentModel(FilamentModel):
    def derive_mesh(self):
        pass

    def derive_cropping_geometry(self):
        pass


# Create a line to test FilamentModel
z = np.linspace(0, 4 * np.pi, 15)
x = np.sin(z)
y = np.cos(x)

xyz = np.column_stack((x, y, z))
line = Line(xyz)

def test_filament_model_instantiation():
    filament = TestFilamentModel(line, 'volume')
    assert isinstance(filament, TestFilamentModel)

def test_filament_model_radius_calculation():
    filament = TestFilamentModel(line, 'volume')
    filament.edge_point = filament.backbone[0] + 0.1
    assert filament.radius is not None

def test_backbone_delta():
    filament = TestFilamentModel(line, 'volume')
    first_point = filament.backbone[0]
    second_point = filament.backbone[1]
    delta = second_point - first_point
    assert_array_almost_equal(delta, filament.backbone_delta[0])
