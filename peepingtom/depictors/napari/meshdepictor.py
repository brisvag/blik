from .naparidepictor import NapariDepictor


class MeshDepictor(NapariDepictor):
    def depict(self):
        # .values cause napari does not like xarray yet
        self._make_surface_layer(self.datablock.vertices.data.values,
                                 self.datablock.faces.data.values,
                                 name=f'{self.name} - mesh')
