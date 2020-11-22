### QUICK SUMMARY
# If you want to generate relion euler angles from matrices which align references to particles
# use:
# matrix2euler zyz intrinsic positive_ccw
# on the transpose of the matrix

# If you want to generate rotation matrices which align references onto aligned particles
# use:
# euler2matrix zyz intrinsic positive_ccw
# then transpose the matrix/matrices


# Understanding RELION euler angles
from numpy.testing import assert_array_almost_equal
from eulerangles import matrix2euler, euler2matrix

# We have a known pair of equivalent Euler angles from the two packages (give identical reconstructions)
dynamo_eulers = [-47.2730, 1.1777, -132.3000]
relion_eulers = [137.7000, 1.1777, 42.7270]

# These pairs MUST give the same rotation matrix (they result in an equivalent operation in each program)
# Taking dynamo as ZXZ extrinsic positive_ccw gives rotm which transforms aligned particle onto ref
dynamo_rotm = euler2matrix(dynamo_eulers, axes='zxz', extrinsic=True, positive_ccw=True)
# the transpose aligns a reference onto an aligned particle
dynamo_ref2particle = dynamo_rotm.T

# The following produces the same rotation matrix as the dynamo rotm, aligns particle onto ref
relion_rotm = euler2matrix(relion_eulers, axes='zyz', intrinsic=True, positive_ccw=True)
# the transpose thus aligns a reference onto an aligns particle
relion_ref2particle = relion_rotm.T

assert_array_almost_equal(dynamo_ref2particle, relion_ref2particle)

