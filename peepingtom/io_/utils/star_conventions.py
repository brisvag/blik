star_types = {
    'dynamo': {
        'coords': ['x', 'y', 'z'],
        'shifts': ['dx', 'dy', 'dz'],
        'angles': ['tdrot', 'tilt', 'narot'],
        'angle_convention': {'axes': 'zxz',
                             'intrinsic': False,
                             'positive_ccw': True,
                             'rotate_reference': False},
        'split_by': 'rlnMicrographName',
    },
    'relion': {
        'coords': [f'rlnCoordinate{axis}' for axis in 'XYZ'],
        'shifts': [f'rlnOrigin{axis}' for axis in 'XYZ'],
        'angles': [f'rlnAngle{angle}' for angle in ('Rot', 'Tilt', 'Psi')],
        'angle_convention': {'axes': 'zyz',
                             'intrinsic': True,
                             'positive_ccw': True,
                             'rotate_reference': False},
        'split_by': 'rlnMicrographName',
    },
    'relion_2d': {
        'coords': [f'rlnCoordinate{axis}' for axis in 'XY'],
        'shifts': [f'rlnOrigin{axis}' for axis in 'XY'],
    },
}
