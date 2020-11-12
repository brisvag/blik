from pathlib import Path

import mrcfile
import numpy as np
import pandas as pd
import starfile

test_data = Path('.')

# Images
im = np.random.random((28, 28)).astype(np.float32)
im_path = test_data / '2d_image.mrc'

vol = np.random.random((28, 28, 28)).astype(np.float32)
vol_path = test_data / '3d_vol.mrc'

with mrcfile.new(im_path, overwrite=True) as mrc:
    mrc.set_data(im)

with mrcfile.new(vol_path, overwrite=True) as mrc:
    mrc.set_data(vol)

# relion star file simple
z = np.linspace(0, 6 * np.pi, 50)
x = 3 * np.sin(z)
y = 3 * np.cos(z)
rot = np.zeros(z.shape[0])
tilt = np.linspace(0, 180, z.shape[0])
psi = rot

star_info = {'rlnCoordinateX': x,
             'rlnCoordinateY': y,
             'rlnCoordinateZ': z,
             'rlnAngleRot': rot,
             'rlnAngleTilt': tilt,
             'rlnAnglePsi': psi}

star = pd.DataFrame.from_dict(star_info)
star['rlnMicrographName'] = 'test_tomo'
star_path = test_data / 'relion_3d_simple.star'
starfile.write(star, star_path)
