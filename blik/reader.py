import numpy as np
from scipy.spatial.transform import Rotation

from naaf import read
from naaf.data import Particles, Image
from naaf.utils.constants import Naaf


def get_reader(path):
    return read_layers


def read_particles(particles):
    layers = []
    coords = np.asarray(particles.data[Naaf.COORD_HEADERS])[:, ::-1]  # order is zyx in napari
    rot = Rotation.concatenate(particles.data[Naaf.ROT_HEADER])
    features = particles.data.drop(columns=Naaf.ALL_HEADERS, errors='ignore')

    pts = (
        coords,
        dict(
            name=f'{particles.name} - particle positions',
            features=features,
            face_color='teal',
            size=10,
            edge_width=0,
            scale=particles.pixel_size,
            shading='spherical',
            metadata={'blik_volume': particles.name}
        ),
        'points',
    )
    layers.append(pts)

    for idx, (ax, color) in enumerate(zip('zyx', 'rgb')):  # order is zyx in napari
        basis = np.zeros(3)
        basis[idx] = 1
        basis_rot = rot.apply(basis)[:, ::-1]  # order is zyx in napari
        vec_data = np.stack([coords, basis_rot], axis=1)
        vec = (
            vec_data,
            dict(
                name=f'{particles.name} - particle orientations ({ax})',
                edge_color=color,
                length=10,
                scale=particles.pixel_size,
                metadata={'blik_volume': particles.name}
            ),
            'vectors',
        )
        layers.append(vec)

    return layers


def read_image(image):
    data = image.data
    if data.ndim == 2:
        data = data[np.newaxis]
    return (
        data,
        dict(
            name=f'{image.name} - image',
            scale=image.pixel_size,
            metadata={'blik_volume': image.name, 'stack': image.stack},
            interpolation='spline36',
        ),
        'image',
    )


def read_layers(*paths, **kwargs):
    data_list = read(*paths, **kwargs)
    layers = []
    for data in data_list:
        if isinstance(data, Particles):
            layers.extend(read_particles(data))
        elif isinstance(data, Image):
            layers.append(read_image(data))

    for lay in layers:
        lay[1]['visible'] = False  # speed up loading
        if lay[1]['scale'] is None:
            # fix until napari#4295 is merged
            lay[1]['scale'] = [1, 1, 1]
    return layers or None
