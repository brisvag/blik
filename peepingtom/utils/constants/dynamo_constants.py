from ..helpers.eulerangle_helper import EulerAngleConvention

dynamo_table_coordinate_headings = ['x', 'y', 'z']
dynamo_table_shift_headings = ['dx', 'dy', 'dz']
dynamo_euler_angle_headings = ['tdrot', 'tilt', 'narot']
dynamo_euler_angle_convention = EulerAngleConvention(axes='zxz', intrinsic=False, positive_ccw=True,
                                                     rotate_reference=False)
