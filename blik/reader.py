import warnings
import numpy as np
from scipy.spatial.transform import Rotation

from cryotypes.image import Image
from cryotypes.poseset import PoseSet, PoseSetDataLabels as PSDL
from naaf import read


def get_reader(path):
    return read_layers


def read_particles(particles):
    layers = []
    for id, df in particles.groupby(PSDL.EXPERIMENT_ID):
        df = df.reset_index(drop=True)

        ndim = 3 if PSDL.POSITION_Z in df else 2
        coords = np.asarray(df[PSDL.POSITION[:ndim]])[:, ::-1]  # order is zyx in napari
        shifts = np.asarray(df[PSDL.SHIFT[:ndim]])[:, ::-1]
        px_size = df[PSDL.PIXEL_SPACING].iloc[0]
        if not px_size:
            warnings.warn('unknown pixel spacing, setting to 1 Angstrom')
            px_size = 1
        scale = np.repeat(px_size, ndim)

        rot = Rotation.concatenate(df[PSDL.ORIENTATION])
        # divide by scale top keep constant size. TODO: remove after vispy 0.12 which fixes this

        pts = (
            coords + shifts,
            dict(
                name=f'{id} - particle positions',
                features=df,
                face_color='teal',
                size=50 / scale,  # TODO: this will be fixed by vispy 0.12!
                edge_width=0,
                scale=scale,
                shading='spherical',
                antialiasing=0,
                metadata={'blik_volume': id},
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
                name=f'{id} - particle orientations',
                edge_color=vec_color,
                length=50 / scale[0],
                scale=scale,
                metadata={'blik_volume': id},
                out_of_slice_display=True,
            ),
            'vectors',
        )
        layers.append(vec)

    return layers


def read_image(image):
    px_size = image.pixel_spacing
    if not px_size:
        warnings.warn('unknown pixel spacing, setting to 1 Angstrom')
        px_size = 1
    return (
        image.data,
        dict(
            name=f'{image.experiment_id} - image',
            scale=[px_size] * image.data.ndim,
            metadata={'blik_volume': image.experiment_id, 'stack': image.stack},
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
        elif isinstance(data, PoseSet):
            layers.extend(read_particles(data))

    for lay in layers:
        lay[1]['visible'] = False  # speed up loading
    return layers or None
