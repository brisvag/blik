from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass
class CroppingGeometry:
    """
    parent : volume file associated with this cropping geometry
    crop_points : positions at which particles should be cropped
    rotation_matrices : (N,3,3) rotation matrices describing rotation of unit vectors to arrive at orientation of particle
    """
    parent: Path
    crop_points: np.ndarray
    rotation_matrices: np.ndarray
