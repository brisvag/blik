import numpy as np


def rotangle2matrix(angle):
    rad = np.deg2rad(np.array(angle).reshape(-1))
    matrices = np.zeros((rad.shape[0], 2, 2), dtype=float)
    cos = np.cos(rad)
    sin = np.sin(rad)
    matrices[:, 0, 0] = cos
    matrices[:, 0, 1] = -sin
    matrices[:, 1, 1] = cos
    matrices[:, 1, 0] = sin
    return matrices.swapaxes(-2, -1)
