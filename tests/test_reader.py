from blik.reader import construct_particle_layer_tuples, get_reader


def test_reader(star_file):
    reader = get_reader(star_file)
    assert callable(reader)

    layer_data_list = reader(star_file)
    assert len(layer_data_list) == 4

    pts = layer_data_list[0]
    assert pts[2] == "points"
    vec = layer_data_list[1]
    assert vec[2] == "vectors"


def test_construct_empty_layers():
    layer_data_list = construct_particle_layer_tuples(
        coords=None,
        features=None,
        scale=1,
        exp_id="test",
    )

    assert len(layer_data_list) == 2

    pts = layer_data_list[0]
    assert pts[2] == "points"
    vec = layer_data_list[1]
    assert vec[2] == "vectors"
