import pandas as pd
import starfile
import eulerangles

from ...utils import _path


def matrix2euler(rotation_matrices, convention):
    """
    convert euler matrices to angles
    """
    # If rotation matrices represent rotations of particle onto reference
    # invert them so that we return matrices which transform reference onto particle
    if convention['rotate_reference'] is False:
        rotation_matrices = rotation_matrices.transpose((0, 2, 1))

    euler_angles = eulerangles.matrix2euler(rotation_matrices,
                                            axes='zyz',
                                            intrinsic=True,
                                            right_handed_rotation=True)
    return euler_angles


def write_star(particleblock, file_path, data_colums=[], overwrite=False):
    """
    write a particle block to disk as a .star file
    data_colums: particleblock properties to include as columns
    """
    coords = particleblock.positions.data
    orientation_matrices = particleblock.orientations.data
    eulers = matrix2euler(orientation_matrices)
    properties = particleblock.properties[data_colums]

    df = pd.DataFrame()

    # TODO
    # x, y, z = coords.T
    # ang1, ang2, ang3 = eulers.T
    # for name, values in zip(column_names, [x, y, z, ang1, ang2, ang3] + properties):
        # df[name] = values

    # path = str(_path(file_path))
    # if not path.endswith('.star'):
        # path = f'{path}.star'
    #starfile.write(df, path, overwrite=overwrite)
