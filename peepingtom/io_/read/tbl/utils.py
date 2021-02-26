from pathlib import Path
import eulerangles


def euler2matrix_dynamo(euler_angles):
    """Convert (n, 3) array of Dynamo euler angles to rotation matrices
    Resulting rotation matrices rotate references into particles
    """
    rotation_matrices = eulerangles.euler2matrix(euler_angles,
                                                 axes='zxz',
                                                 intrinsic=False,
                                                 right_handed_rotation=True)

    rotation_matrices = rotation_matrices.swapaxes(-2, -1)
    return rotation_matrices


def name_from_volume(volume_identifier):
    """Generate ParticleBlock name from volume identifier from dataframe
    """
    if isinstance(volume_identifier, int):
        return str(volume_identifier)
    elif isinstance(volume_identifier, str):
        return Path(volume_identifier).stem
