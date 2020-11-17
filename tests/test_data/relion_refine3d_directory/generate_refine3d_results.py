import mrcfile
import numpy as np
import pandas as pd
import starfile
from eulerangles import matrix2euler

from peepingtom.utils.helpers.linalg_helper import align_vectors

# coords for helix along z varying in time
t = np.linspace(0, 6 * np.pi, 25).reshape(1, -1)
z = np.linspace(0.1, 6 * np.pi+0.1, 50).reshape(-1, 1)
x = 3 * np.sin(z + t)
y = 3 * np.cos(z + t)

# helix backbone for orientation calculation
x_backbone = np.zeros(z.shape[0])
y_backbone = np.zeros(z.shape[0])

xyz_backbone = np.column_stack([x_backbone, y_backbone, z])

# add some displacements
x_t = x + np.random.normal(0, 0.5, (50, 25))
y_t = y + np.random.normal(0, 0.5, (50, 25))
z_t = z + np.random.normal(0, 0.2, (50, 25))

# define function to calculate euler angles for star file
def xyz_to_rln_eulers(xyz):
    orientation_vectors = xyz - xyz_backbone
    orientation_vectors_normalised = orientation_vectors / np.linalg.norm(orientation_vectors, axis=1).reshape((-1, 1))
    unit_z = np.array([0, 0, 1])

    # calculate rotation matrices to align unit vector to direction away from backbone
    rotation_matrices = align_vectors(unit_z, orientation_vectors_normalised)

    # calculate eulers from rotation matrices
    euler_angles_rln = matrix2euler(rotation_matrices, target_axes='ZYZ', target_positive_ccw=True, target_intrinsic=True)
    rot = euler_angles_rln[:, 0]
    tilt = euler_angles_rln[:, 1]
    psi = euler_angles_rln[:, 2]

    return rot, tilt, psi


# generate star files
for ite in range(25):
    xyz = np.column_stack([x_t[:, ite], y_t[:, ite], z_t[:, ite]])
    rot, tilt, psi = xyz_to_rln_eulers(xyz)
    star_info = {'rlnCoordinateX': x_t[:, ite],
             'rlnCoordinateY': y_t[:, ite],
             'rlnCoordinateZ': z_t[:, ite],
             'rlnAngleRot': rot,
             'rlnAngleTilt': tilt,
             'rlnAnglePsi': psi}

    star = pd.DataFrame.from_dict(star_info)
    star['rlnMicrographName'] = 'test_tomo'
    starfile.write(star, f'run_ite{ite:03d}_data.star')