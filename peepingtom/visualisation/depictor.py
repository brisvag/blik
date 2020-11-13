"""
Depictor interfaces data classes to napari
"""

from types import MethodType

import numpy as np
import napari
from napari.components.layerlist import LayerList

from ..base import DataBlock, GroupBlock, PointBlock, LineBlock, OrientationBlock, ImageBlock, ParticleBlock


class Depictor:
    """
    Depictors are DataBlock or GroupBlock wrappers able to display their contents in napari
    """
    def __init__(self, datablock, peeper, name='NoName'):
        self.datablock = datablock

        # this hack updates DataBlock.updated() with a new version that calls Depictor.update()
        def updated_patch(slf):
            slf.depictor.update()
        if isinstance(self.datablock, GroupBlock):
            for child in self.datablock.children:
                child.updated = MethodType(updated_patch, child)
                child.depictor = self
        self.datablock.updated = MethodType(updated_patch, self.datablock)
        # hook self to the datablock
        self.datablock.depictor = self

        self.name = name
        self.peeper = peeper
        self.layers = LayerList()

    @property
    def viewer(self):
        return self.peeper.viewer

    def draw(self, viewer=None, remake_layers=False):
        """
        creates a new napari viewer if not present
        displays the contents of the datablock
        """
        # create a new viewer if necessary
        if viewer is None:
            viewer = self.viewer
        if self.layers and not remake_layers:
            for layer in self.layers:
                self.viewer.add_layer(layer)

    def hide(self, layers=None, delete_layers=False):
        """
        layer_id can be the index or name of a layer or a list of ids
        """
        if layers is None:
            layers = [l for l in self.layers]
        if not isinstance(layers, list):
            layers = [layers]
        for l in layers:
            if l in self.layers:
                self.viewer.layers.remove(l)
                if delete_layers:
                    self.layers.remove(l)

    def update(self):
        pass


class ImageDepictor(Depictor):
    def draw(self, image_kwargs={}, **kwargs):
        super().draw(**kwargs)

        ikwargs = {}
        ikwargs.update(image_kwargs)

        layer = self.viewer.add_image(self.datablock.data,
                                      name=f'{self.name} - image',
                                      **ikwargs)
        self.layers.append(layer)


class ParticleDepictor(Depictor):
    def draw(self, point_kwargs={}, vector_kwargs={}, **kwargs):
        super().draw(**kwargs)

        pkwargs = {'size': 3}
        vkwargs = {'length': 10}

        pkwargs.update(point_kwargs)
        vkwargs.update(vector_kwargs)

        p_layer = self.viewer.add_points(self.datablock.positions.zyx,
                                         name=f'{self.name} - particle positions',
                                         properties=self.datablock.properties.data,
                                         **pkwargs)
        self.layers.append(p_layer)

        # get positions and 'projection' vectors
        positions = self.datablock.positions.zyx
        unit_z_rotated_order_xyz = self.datablock.orientations.oriented_vectors('z').reshape((-1, 3))
        unit_z_rotated_order_zyx = unit_z_rotated_order_xyz[:, ::-1]

        napari_vectors = np.stack([positions,
                                   unit_z_rotated_order_zyx],
                                  # TODO: fix why x and not z!
                                  axis=1)
        v_layer = self.viewer.add_vectors(napari_vectors,
                                        name=f'{self.name} - particle orientations',
                                        **vkwargs)
        self.layers.append(v_layer)

    @property
    def point_layer(self):
        return self.layers[f'{self.name} - particle positions']

    @property
    def vector_layer(self):
        return self.layers[f'{self.name} - particle orientations']

    def update(self):
        try:
            self.point_layer.properties = {k: v for k, v in self.datablock.properties.data.items()
                                           if len(v) == len(self.datablock.positions.data)}
        except KeyError:
            # happens if layers do not exist: just pass
            pass


class Old:
    def draw(self, viewer=None, **kwargs):
        super().draw(viewer=viewer)
        for depictor in self.depictors:
            depictor.draw(viewer=self.viewer, **kwargs)

    def update():
        pass

    @property
    def particles(self):
        return [p for p in self.data_block if isinstance(p, ParticleBlock)]

    @property
    def particle_positions(self):
        return [p.coords for p in self.particles]

    @property
    def particle_vectors(self):
        return [p.ori_as_vectors() for p in self.particles]

    @property
    def particle_vectors_napari(self):
        stacked = []
        for coords, vectors in zip(self.particle_positions, self.particle_vectors):
            stacked.append(np.stack([coords, vectors], axis=1))
        return stacked

    @property
    def images(self):
        return [i for i in self.data_block if isinstance(i, ImageBlock)]

    @property
    def image_data(self):
        return [i.data for i in self.images]

    @property
    def image_shapes(self):
        return [i.shape for i in self.image_data]

