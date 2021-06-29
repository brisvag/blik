import pandas as pd
import starfile
import eulerangles


def matrix2euler(rotation_matrices):
    """
    convert euler matrices to angles
    """
    # invert them so that we return matrices which transform reference onto particle
    rotation_matrices = rotation_matrices.transpose((0, 2, 1))

    euler_angles = eulerangles.matrix2euler(rotation_matrices,
                                            axes='zyz',
                                            intrinsic=True,
                                            right_handed_rotation=True)
    return euler_angles


def matrix2rotangle(rotation_matrices):
    raise NotImplementedError


coord_headings = {
    '3d': [f'rlnCoordinate{axis}' for axis in 'XYZ'],
    '2d': [f'rlnCoordinate{axis}' for axis in 'XY']
}

euler_headings = [f'rlnAngle{angle}' for angle in ('Rot', 'Tilt', 'Psi')]

angle_heading = ['rlnAnglePsi']


def write_star(particleblock, file_path, data_colums=None, overwrite=False):
    """
    write a particle block to disk as a .star file
    data_colums: particleblock properties to include as columns
    """
    coords = particleblock.positions.data
    dim = 3 if particleblock.is_3D else 2
    orientation_matrices = particleblock.orientations.data
    if data_colums is not None:
        properties = particleblock.properties.data[data_colums].to_numpy()
    else:
        data_colums = []
        properties = []

    df = pd.DataFrame()

    if dim == 3:
        x, y, z = coords.T
        eulers = matrix2euler(orientation_matrices)
        ang1, ang2, ang3 = eulers.T
        column_names = coord_headings['3d'] + euler_headings + data_colums
        for name, values in zip(column_names, [x, y, z, ang1, ang2, ang3] + properties):
            df[name] = values
    else:
        x, y = coords.T
        rotangle = matrix2rotangle(orientation_matrices)
        psi = rotangle.T
        column_names = coord_headings['2d'] + angle_heading + data_colums
        for name, values in zip(column_names, [x, y, psi] + properties):
            df[name] = values

    path = file_path
    if not path.suffix:
        path = str(path) + '.star'
    starfile.write(df, path, overwrite=overwrite)
