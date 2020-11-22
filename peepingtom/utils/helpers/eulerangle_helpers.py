### QUICK SUMMARY
# If you want to generate relion euler angles from matrices which align references to particles
# use:
# matrix2euler zyz intrinsic positive_ccw
# on the transpose of the matrix

# If you want to generate rotation matrices which align references onto aligned particles
# use:
# euler2matrix zyz intrinsic positive_ccw
# then transpose the matrix/matrices


# If you want to generate dynamo euler angles from matrices which align references to particles
# use:
# matrix2euler zxz intrinsic positive_ccw
# on the transpose of the matrix

# If you want to generate matrices which align references to particles from dynamo euler angles
# use:
# euler2matrix zxz extrinsic positive_ccw
# then transpose the matrix/matrices

import numpy as np
from eulerangles import matrix2euler, euler2matrix


def relion_eulers_to_matrices(euler_angles: np.ndarray):
    """
    Convert RELION euler angles (Rot, Tilt, Psi) into rotation matrices
    which rotate references onto aligned particles

    Parameters
    ----------
    euler_angles : (n, 3) array of float
                   Rot, Tilt, Psi from RELION

    Returns
    -------
    rotation_matrices : (n, 3, 3) array of float
                        rotation matrices which premultiply vectors in the reference frame of the reference
                        to transform them onto the 'aligned' particle

    """
    # Get the rotation matrices which transform the aligned particles onto the reference
    rotation_matrices = euler2matrix(euler_angles, axes='zyz', intrinsic=True, positive_ccw=True)

    # Invert the matrix (by transposing) to find matrices which transform reference onto aligned particles
    rotation_matrices = rotation_matrices.transpose((0, 2, 1))

    return rotation_matrices


def dynamo_eulers_to_matrices(euler_angles: np.ndarray):
    """
    Convert Dynamo euler angles (tdrot, tilt, narot) into rotation matrices
    which rotate references onto aligned particles

    Parameters
    ----------
    euler_angles : (n, 3) array of float
                   tdrot, tilt, narot from Dynamo

    Returns
    -------
    rotation_matrices : (n, 3, 3) array of float
                        rotation matrices which premultiply vectors in the reference frame of the reference
                        to transform them onto the 'aligned' particle

    """
    # Get the rotation matrices which transform the aligned particles onto the reference
    rotation_matrices = euler2matrix(euler_angles, axes='zxz', extrinsic=True, positive_ccw=True)

    # Invert the matrix (by transposing) to find matrices which transform reference onto aligned particles
    rotation_matrices = rotation_matrices.transpose((0, 2, 1))

    return rotation_matrices


def matrices_to_relion_eulers(rotation_matrices: np.ndarray):
    """
    Convert rotation matrices which rotate references onto aligned particles
    into RELION euler angles (Rot, Tilt, Psi)

    Parameters
    ----------

    rotation_matrices : (n, 3, 3) array of float
                        rotation matrices which premultiply vectors in the reference frame of the reference
                        to transform them onto the 'aligned' particle
    Returns
    -------
    euler_angles : (n, 3) array of float
                   Rot, Tilt, Psi from RELION

    """
    # Invert the matrices (by transposing) to find matrices which transform reference onto aligned particles
    rotation_matrices = rotation_matrices.transpose((0, 2, 1))

    # Get the RELION euler angles
    euler_angles = matrix2euler(rotation_matrices, target_axes='zyz', target_intrinsic=True, target_positive_ccw=True)

    return euler_angles


def matrices_to_dynamo_eulers(rotation_matrices: np.ndarray):
    """
    Convert rotation matrices which rotate references onto aligned particles
    into Dynamo euler angles (tdrot, tilt, narot)

    Parameters
    ----------
    rotation_matrices : (n, 3, 3) array of float
                        rotation matrices which premultiply vectors in the reference frame of the reference
                        to transform them onto the 'aligned' particle

    Returns
    -------

    euler_angles : (n, 3) array of float
                   tdrot, tilt, narot from Dynamo
    """
    # Invert the matrix (by transposing) to find matrices which transform reference onto aligned particles
    rotation_matrices = rotation_matrices.transpose((0, 2, 1))

    # Get the rotation matrices which transform the aligned particles onto the reference
    euler_angles = matrix2euler(rotation_matrices, axes='zxz', extrinsic=True, positive_ccw=True)

    return euler_angles
