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
    features = particles.data.drop(columns=Naaf.COORD_HEADERS, errors='ignore')
    # divide by scale top keep constant size. TODO: remove after vispy 0.12 which fixes this
    scale = particles.pixel_size if particles.pixel_size is not None else np.array([1, 1, 1])

    pts = (
        coords,
        dict(
            name=f'{particles.name} - particle positions',
            features=features,
            face_color='teal',
            size=50 / scale,
            edge_width=0,
            scale=scale,
            shading='spherical',
            antialiasing=0,
            metadata={'blik_volume': particles.name},
            out_of_slice_display=True,
        ),
        'points',
    )
    layers.append(pts)

    vec_data = np.empty((len(coords) * 3, 2, 3))
    vec_color = np.empty((len(coords) * 3, 3))
    for idx, (ax, color) in enumerate(zip('xyz', 'rgb')):
        basis = np.zeros(3)
        basis[idx] = 1  # also acts as color (rgb)
        basis_rot = rot.apply(basis)[:, ::-1]  # order is zyx in napari
        vec_data[idx::3] = np.stack([coords, basis_rot], axis=1)
        vec_color[idx::3] = basis

    vec = (
        vec_data,
        dict(
            name=f'{particles.name} - particle orientations',
            edge_color=vec_color,
            length=50 / scale[0],
            scale=scale,
            metadata={'blik_volume': particles.name},
            out_of_slice_display=True,
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
            interpolation2d='spline36',
            interpolation3d='linear',
            rendering='average',
            depiction='plane',
            blending='translucent',
            plane=dict(thickness=5),
        ),
        'image',
    )


def read_layers(*paths, **kwargs):
    data_list = read(*paths, **kwargs)
    layers = []
    # sort so we get images first, better for some visualization circumstances
    for data in sorted(data_list, key=lambda x: not isinstance(x, Image)):
        if isinstance(data, Image):
            layers.append(read_image(data))
        elif isinstance(data, Particles):
            layers.extend(read_particles(data))

    for lay in layers:
        lay[1]['visible'] = False  # speed up loading
    return layers or None
