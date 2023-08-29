import mrcfile
import numpy as np
import pandas as pd
import pytest
import starfile


@pytest.fixture(scope="session")
def star_file(tmp_path_factory):
    df = pd.DataFrame(
        {
            "rlnCoordinateX": [1, 1],
            "rlnCoordinateY": [2, 2],
            "rlnCoordinateZ": [3, 3],
            "rlnOriginX": [0.1, 0.1],
            "rlnOriginY": [0.2, 0.2],
            "rlnOriginZ": [0.3, 0.3],
            "rlnAngleRot": [0, 0],
            "rlnAngleTilt": [0, 90],
            "rlnAnglePsi": [90, 0],
            "rlnMicrographName": ["a_1", "a_2"],
            "feature": ["x", "y"],
        }
    )
    file_path = tmp_path_factory.mktemp("data") / "test.star"
    starfile.write(df, file_path)
    return file_path


@pytest.fixture(scope="session")
def mrc_file(tmp_path_factory):
    file_path = tmp_path_factory.mktemp("data") / "test.mrc"
    data = np.zeros((10, 10, 10), np.float32)
    data[5, 5, 5] = 1
    with mrcfile.new(file_path, data) as mrc:
        mrc.set_data(data)
    return file_path
