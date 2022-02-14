import pandas as pd
import starfile
from blik._plugin.reader import get_reader


def test_reader(tmp_path):
    df = pd.DataFrame({
        'rlnCoordinateX': [1, 1],
        'rlnCoordinateY': [2, 2],
        'rlnCoordinateZ': [3, 3],
        'rlnOriginX': [0.1, 0.1],
        'rlnOriginY': [0.2, 0.2],
        'rlnOriginZ': [0.3, 0.3],
        'rlnAngleRot': [0, 0],
        'rlnAngleTilt': [0, 90],
        'rlnAnglePsi': [90, 0],
        'rlnMicrographName': ['a', 'b'],
        'feature': ['x', 'y'],
    })
    file_path = tmp_path / 'test.star'
    starfile.write(df, file_path)

    reader = get_reader(file_path)
    assert callable(reader)

    layer_data_list = reader(file_path)
    assert len(layer_data_list) == 8

    pts = layer_data_list[0]
    assert pts[2] == 'points'
    vec = layer_data_list[2]
    assert vec[2] == 'vectors'
