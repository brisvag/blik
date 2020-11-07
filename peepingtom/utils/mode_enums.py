from enum import Enum


class ImageType(Enum):
    image = 0
    multi_frame_micrograph = 1
    micrograph = 2
    tilt_series = 3
    tomogram = 4
    cross_correlation_volume = 5


class ModelType(Enum):
    particle = 0
    dipole = 1
    vesicle = 2
    filament = 3
    surface = 4
    crystal = 5