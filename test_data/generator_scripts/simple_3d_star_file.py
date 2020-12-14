import numpy as np
import pandas as pd
import starfile

from peepingtom.utils.helpers.eulerangle_helper import EulerAngleHelper
from peepingtom.utils.helpers.linalg_helper import align_vectors

from .constants import test_data_dir

# relion star file simple
# coords for helix along z
z = np.linspace(0.1, 6 * np.pi + 0.1, 50)
x = 3 * np.sin(z)
y = 3 * np.cos(z)

# backbone along center of helix
x_backbone = np.zeros(z.shape[0])
y_backbone = np.zeros(z.shape[0])

xyz = np.column_stack([x, y, z])
xyz_backbone = np.column_stack([x_backbone, y_backbone, z])

# calculate directions from backbone to points on helix
orientation_vectors = xyz - xyz_backbone
orientation_vectors_norm = orientation_vectors / np.linalg.norm(orientation_vectors, axis=1).reshape((-1, 1))
unit_z = np.array([0, 0, 1])

# calculate rotation matrices to align unit vector to direction away from backbone
rotation_matrices = align_vectors(unit_z, orientation_vectors_norm)

# calculate eulers from rotation matrices
euler_angles_rln = EulerAngleHelper(rotation_matrices=rotation_matrices).matrix2euler('relion')

rot = euler_angles_rln[:, 0]
tilt = euler_angles_rln[:, 1]
psi = euler_angles_rln[:, 2]

star_info = {'rlnCoordinateX': x,
             'rlnCoordinateY': y,
             'rlnCoordinateZ': z,
             'rlnAngleRot': rot,
             'rlnAngleTilt': tilt,
             'rlnAnglePsi': psi}

star = pd.DataFrame.from_dict(star_info)
star['rlnMicrographName'] = 'test_tomo'
star_path = test_data_dir / 'relion_3d_simple.star'
starfile.write(star, star_path)
