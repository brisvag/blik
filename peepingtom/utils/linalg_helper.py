import numpy as np


def align_vectors(a: np.ndarray, b: np.ndarray):
    """
    Find array of rotation matrices r such that r @ a = b when a and b are arrays of normalised vectors
    implementation designed to avoid trig calls
    based on https://iquilezles.org/www/articles/noacos/noacos.htm
    :param a: normalised vector(s) of length 3
    :param b: normalised vector(s) of length 3
    :return: rotation matrix
    """
    # setup
    a = a.reshape(-1, 3)
    b = b.reshape(-1, 3)
    n_vectors = max(a.shape[0], b.shape[0])

    # cross product to find axis about which rotation should occur
    axis = np.cross(a, b, axis=1)
    # dot product equals cosine of angle between normalised vectors
    cos_angle = np.einsum('ij, ij -> i', a, b)
    # k is a constant which appears as a factor in the rotation matrix
    k = 1 / (1 + cos_angle)

    # construct rotation matrix
    r = np.empty((n_vectors, 3, 3))
    r[:, 0, 0] = (axis[:, 0] * axis[:, 0] * k) + cos_angle
    r[:, 0, 1] = (axis[:, 1] * axis[:, 0] * k) - axis[:, 2]
    r[:, 0, 2] = (axis[:, 2] * axis[:, 0] * k) + axis[:, 1]
    r[:, 1, 0] = (axis[:, 0] * axis[:, 1] * k) + axis[:, 2]
    r[:, 1, 1] = (axis[:, 1] * axis[:, 1] * k) + cos_angle
    r[:, 1, 2] = (axis[:, 2] * axis[:, 1] * k) - axis[:, 0]
    r[:, 2, 0] = (axis[:, 0] * axis[:, 2] * k) - axis[:, 1]
    r[:, 2, 1] = (axis[:, 1] * axis[:, 2] * k) + axis[:, 0]
    r[:, 2, 2] = (axis[:, 2] * axis[:, 2] * k) + cos_angle

    return r
