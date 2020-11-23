from ..helpers.eulerangle_helper import EulerAngleConvention

relion_coordinate_headings_2d = [f'rlnCoordinate{axis}' for axis in 'XY']
relion_shift_headings_2d = [f'rlnOrigin{axis}' for axis in 'XY']
relion_coordinate_headings_3d = [f'rlnCoordinate{axis}' for axis in 'XYZ']
relion_shift_headings_3d = [f'rlnOrigin{axis}' for axis in 'XYZ']
relion_euler_angle_headings = [f'rlnAngle{angle}' for angle in ('Rot', 'Tilt', 'Psi')]
relion_euler_angle_convention = EulerAngleConvention(axes='zyz', intrinsic=True, positive_ccw=True,
                                                     rotate_reference=False)
