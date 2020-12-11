import pandas as pd
import starfile
import eulerangles

from ...utils import _path, star_types


def matrix2euler(rotation_matrices, convention):
    """
    convert euler matrices to angles
    """
    # If rotation matrices represent rotations of particle onto reference
    # invert them so that we return matrices which transform reference onto particle
    if convention['rotate_reference'] is False:
        rotation_matrices = rotation_matrices.transpose((0, 2, 1))

    euler_angles = eulerangles.matrix2euler(rotation_matrices,
                                            target_axes=convention['axes'],
                                            target_intrinsic=convention['intrinsic'],
                                            target_positive_ccw=convention['positive_ccw'])
    return euler_angles


def write_star(particleblock, file_path, star_type='relion', data_colums=[], overwrite=False):
    """
    write a particle block to disk as a .star file
    star_type: one of the supported starfile types
    data_colums: particleblock proerties to include as columns
    """
    coords = particleblock.positions.data
    orientation_matrices = particleblock.orientations.data
    eulers = matrix2euler(orientation_matrices, star_types[star_type]['angle_convention'])
    properties = [values for name, values in particleblock.properties.items() if name in data_colums]

    df = pd.DataFrame()
    column_names = star_types[star_type]['coords'] + star_types[star_type]['angles'] + data_colums
    x, y, z = coords.T
    ang1, ang2, ang3 = eulers.T
    for name, values in zip(column_names, [x, y, z, ang1, ang2, ang3] + properties):
        df[name] = values

    path = str(_path(file_path))
    if not path.endswith('.star'):
        path = f'{path}.star'
    starfile.write(df, path, overwrite=overwrite)
