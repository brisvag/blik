import xarray as xr

from .naparidepictor import NapariDepictor
from ...utils.colors import distinct_colors


class ParticleDepictor(NapariDepictor):
    def depict(self, rescale=True):
        pkwargs = {'size': 3}
        vkwargs = {'length': 10}

        pos, ori = self.get_positions_and_orientations(rescale=rescale)

        self._make_points_layer(pos,
                                name=f'{self.name} - particle positions',
                                scale=self.datablock.pixel_size,
                                properties=self.get_properties(),
                                **pkwargs)

        self._make_vectors_layer(ori.values,  # need to use values cause napari complains
                                 name=f'{self.name} - particle orientations',
                                 scale=self.datablock.pixel_size,
                                 **vkwargs)

    def get_properties(self):
        return self.datablock.properties.data

    def get_positions_and_orientations(self, rescale=True):
        positions = self.datablock.positions.as_zyx()
        # rescale if needed
        if 0 <= positions.min() <= positions.max() <= 1 and rescale:
            peeper = self.datablock.peeper
            if peeper:
                same_volume = peeper.volumes[self.datablock.volume]
                for db in same_volume:
                    from ...datablocks import ImageBlock
                    if isinstance(db, ImageBlock):
                        positions *= db.shape
                        break

        v_axis = self.datablock.positions.data.spatial[-1]  # y or z
        v_rotated = self.datablock.orientations.oriented_vectors(v_axis).loc[:, list('zyx')]

        stacked = xr.concat([positions, v_rotated], dim='vector').transpose('n', 'vector', 'spatial')
        return positions, stacked

    @property
    def points(self):
        return self.layers[0]

    @property
    def vectors(self):
        return self.layers[1]

    def color_by_categorical_property(self, property, colors=None):
        if self.layers:
            self.points.face_color = property
            self.points.face_color_cycle = colors or distinct_colors

    def update(self):
        if self.layers:
            pos, ori = self.get_positions_and_orientations()
            self.points.data = pos.values  # workaround for xarray
            self.vectors.data = ori.values  # workaround for xarray
            self.points.properties = self.get_properties()
