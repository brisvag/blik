import pandas as pd
import starfile

from blik.io_.reading.star import read_star
from blik.datablocks import ParticleBlock


def test_read_relion30_3d(tmp_path):
    df = pd.DataFrame({
        'rlnCoordinateX': [1, 2],
        'rlnCoordinateY': [1, 2],
        'rlnCoordinateZ': [1, 2],
        'rlnOriginX': [1, 2],
        'rlnOriginY': [1, 2],
        'rlnOriginZ': [1, 2],
        'rlnAngleRot': [1, 2],
        'rlnAngleTilt': [1, 2],
        'rlnAnglePsi': [1, 2],
        'rlnMicrographName': ['a', 'b'],
    })
    file_path = tmp_path / 'test.star'
    starfile.new(df, file_path)

    particleblocks = read_star(file_path, name_regex=r'\w')
    assert all(isinstance(pb, ParticleBlock) for pb in particleblocks)
    assert particleblocks[0].name == 'a'


def test_read_relion31_3d(tmp_path):
    df_optics = pd.DataFrame({
        'rlnOpticsGroup': [1],
        'rlnImagePixelSize': [1],
    })
    df_particles = pd.DataFrame({
        'rlnCoordinateX': [1, 2],
        'rlnCoordinateY': [1, 2],
        'rlnCoordinateZ': [1, 2],
        'rlnOriginXAngst': [1, 2],
        'rlnOriginYAngst': [1, 2],
        'rlnOriginZAngst': [1, 2],
        'rlnAngleRot': [1, 2],
        'rlnAngleTilt': [1, 2],
        'rlnAnglePsi': [1, 2],
        'rlnMicrographName': ['a', 'b'],
        'rlnOpticsGroup': [1, 1],
    })
    data_dict = {'optics': df_optics, 'particles': df_particles}
    file_path = tmp_path / 'test.star'
    starfile.new(data_dict, file_path)

    particleblocks = read_star(file_path)
    assert all(isinstance(pb, ParticleBlock) for pb in particleblocks)
