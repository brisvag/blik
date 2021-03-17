import xarray as xr

from .naparidepictor import NapariDepictor


class ParticleDepictor(NapariDepictor):
    def depict(self):
        pkwargs = {'size': 3}
        vkwargs = {'length': 10}

        pos, ori = self.get_positions_and_orientations()

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

    def get_positions_and_orientations(self):
        positions = self.datablock.positions.as_zyx()
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

    def update(self):
        pos, ori = self.get_positions_and_orientations()
        self.points.data = pos.values  # workaround for xarray
        self.vectors.data = ori.values  # workaround for xarray
        self.points.properties = self.get_properties()
