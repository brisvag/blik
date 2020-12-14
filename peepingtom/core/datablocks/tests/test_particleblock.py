import numpy as np

# test data for ParticleBlock
# positions
z = np.linspace(0, 6 * np.pi, 50)
x = 3 * np.sin(z)
y = 3 * np.cos(z)
xyz = np.column_stack([x, y, z])
