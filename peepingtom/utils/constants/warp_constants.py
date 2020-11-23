from ..helpers.eulerangle_helper import EulerAngleConvention

warp_euler_angle_convention = EulerAngleConvention(axes='zyz', intrinsic=True, positive_ccw=True,
                                                   rotate_reference=False)
